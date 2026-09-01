import { useEffect, useRef, useCallback } from 'react'

/*
 * useProctoring — Live proctoring for job interviews only.
 *
 * All detection runs in the browser:
 *   - Face detection:  MediaPipe Face Detection (WASM)
 *   - Gaze tracking:   MediaPipe Face Mesh (WASM)
 *   - Tab/visibility:  JS Visibility API + window blur (deduped)
 *   - Paste events:    document.onpaste
 *   - Right-click:     document.oncontextmenu
 *   - DevTools:        debugger timing heuristic
 *   - Typing speed:    keydown timestamp analysis (all keystrokes)
 *   - Audio activity:  Web Audio API with candidate voice baseline
 *
 * Candidate sees nothing. Flags stored silently.
 */

const DEFAULT_WEIGHTS = {
  face_absent_per_10s: 5,
  multiple_faces: 15,
  gaze_off_screen: 3,
  second_voice: 10,
  tab_switch: 8,
  paste_event: 10,
  code_typed_too_fast: 20,
  right_click: 2,
  devtools: 15,
}

const FRAME_INTERVAL_MS = 2000
const GAZE_OFF_THRESHOLD_MS = 3000
const AUDIO_ENERGY_THRESHOLD = 0.08
const TYPING_SPEED_WPM_SUSPICIOUS = 120
const PASTE_SIZE_THRESHOLD = 30
const VOICE_BASELINE_DURATION_MS = 5000
const GAZE_DEDUP_WINDOW_MS = 10000
const FEATURE_SAMPLE_INTERVAL_MS = 1000  // 1 sample/sec for storage
const LANDMARK_DOWNSAMPLE = 5            // store every 5th landmark (468→94 points)

export default function useProctoring(active, options = {}) {
  const weights = { ...DEFAULT_WEIGHTS, ...options.weights }

  const flagsRef = useRef({
    face_absent_seconds: 0,
    multiple_faces_count: 0,
    gaze_off_screen_count: 0,
    second_voice_count: 0,
    tab_switch_count: 0,
    paste_event_count: 0,
    code_typed_too_fast: false,
    right_click_count: 0,
    devtools_opened: false,
    camera_denied: false,
  })

  const timelineRef = useRef([])
  const startTimeRef = useRef(null)
  const frameTimerRef = useRef(null)
  const lastFrameTimeRef = useRef(null)
  const streamRef = useRef(null)
  const videoRef = useRef(null)
  const gazeAwaySinceRef = useRef(null)
  const lastGazeEventRef = useRef(0)
  const lastKeystrokeRef = useRef(null)
  const keystrokeCountRef = useRef(0)
  const totalKeystrokesRef = useRef(0)
  const wpmCheckTimerRef = useRef(null)
  const audioCtxRef = useRef(null)
  const analyserRef = useRef(null)
  const audioTimerRef = useRef(null)
  const mediaPipeDetectorRef = useRef(null)
  const mediaPipeLandmarkerRef = useRef(null)
  const audioBaselineRef = useRef(null)
  const voiceActiveRef = useRef(false)
  const voiceStartRef = useRef(null)
  const lastBlurRef = useRef(0)

  // ── Feature vector collection (for post-interview analysis) ──────
  const featuresRef = useRef({
    face_landmarks: [],    // downsampled face landmarks per second
    gaze_vectors: [],      // [x, y] gaze direction per second
    head_pose: [],         // [pitch, yaw, roll] per second
    audio_features: [],    // {energy, pitch_proxy, speech_ratio} per second
    eye_contact_pct: 0,    // computed at end
    total_frames: 0,
  })
  const featureTimerRef = useRef(null)
  const audioEnergyHistoryRef = useRef([])

  const elapsed = useCallback(() => {
    if (!startTimeRef.current) return 0
    return Math.floor((Date.now() - startTimeRef.current) / 1000)
  }, [])

  const addTimelineEvent = useCallback((event, extra = {}) => {
    const now = Date.now()
    // Dedup: suppress same event within GAZE_DEDUP_WINDOW_MS
    const last = timelineRef.current[timelineRef.current.length - 1]
    if (last && last.event === event && (now - (last._rawTime || 0)) < GAZE_DEDUP_WINDOW_MS) {
      last.duration = Math.round((now - (last._rawTime || 0)) / 1000)
      return
    }
    timelineRef.current.push({ t: elapsed(), event, _rawTime: now, ...extra })
  }, [elapsed])

  // ── Face detection via MediaPipe ────────────────────────────────
  const detectFace = useCallback(async () => {
    if (!videoRef.current || videoRef.current.readyState < 2) return
    try {
      if (!mediaPipeDetectorRef.current) {
        const vision = await import(/* @vite-ignore */ 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/+esm')
        const { FaceDetector, FilesetResolver } = vision
        const filesetResolver = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm'
        )
        mediaPipeDetectorRef.current = await FaceDetector.createFromOptions(filesetResolver, {
          baseOptions: { modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short/float16/1/blaze_face_short.tflite', delegate: 'GPU' },
          runningMode: 'VIDEO',
          minDetectionConfidence: 0.5,
        })
      }
      const result = mediaPipeDetectorRef.current.detectForVideo(videoRef.current, performance.now())
      const faces = result.detections || []

      // Use actual elapsed time since last frame, not hardcoded 2
      const now = Date.now()
      const frameDelta = lastFrameTimeRef.current ? Math.round((now - lastFrameTimeRef.current) / 1000) : 2
      lastFrameTimeRef.current = now

      if (faces.length === 0) {
        flagsRef.current.face_absent_seconds += frameDelta
        addTimelineEvent('face_absent', { duration: frameDelta })
      } else if (faces.length > 1) {
        flagsRef.current.multiple_faces_count++
        addTimelineEvent('multiple_faces', { count: faces.length })
      }

      // Face too far check
      if (faces.length > 0) {
        const box = faces[0].boundingBox
        const faceTooSmall = box.width / videoRef.current.videoWidth < 0.15
        if (faceTooSmall) {
          addTimelineEvent('face_too_far')
        }
      }

      // Feature: face bounding box for non-verbal analysis
      if (faces.length > 0) {
        const box = faces[0].boundingBox
        featuresRef.current.face_landmarks.push({
          t: elapsed(),
          bbox: {
            x: Math.round(box.xMin * 1000) / 1000,
            y: Math.round(box.yMin * 1000) / 1000,
            w: Math.round(box.width * 1000) / 1000,
            h: Math.round(box.height * 1000) / 1000,
          },
        })
        featuresRef.current.total_frames++
      }
    } catch {
      // MediaPipe not loaded or camera error — skip silently
    }
  }, [addTimelineEvent])

  // ── Iris / gaze via MediaPipe Face Mesh ──────────────────────────
  const detectGaze = useCallback(async () => {
    if (!videoRef.current || videoRef.current.readyState < 2) return
    try {
      if (!mediaPipeLandmarkerRef.current) {
        const vision = await import(/* @vite-ignore */ 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/+esm')
        const { FaceLandmarker, FilesetResolver } = vision
        const filesetResolver = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm'
        )
        mediaPipeLandmarkerRef.current = await FaceLandmarker.createFromOptions(filesetResolver, {
          baseOptions: { modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task', delegate: 'GPU' },
          runningMode: 'VIDEO',
          numFaces: 1,
          outputFaceBlendshapes: false,
        })
      }
      const result = mediaPipeLandmarkerRef.current.detectForVideo(videoRef.current, performance.now())
      const landmarks = result.faceLandmarks?.[0]
      if (!landmarks) return

      // Use iris landmarks (468-477) for accurate gaze if available
      const leftIris = landmarks[468]
      const rightIris = landmarks[473]
      const leftEyeInner = landmarks[133]
      const leftEyeOuter = landmarks[33]
      const rightEyeInner = landmarks[362]
      const rightEyeOuter = landmarks[263]

      let gazeX, gazeY
      if (leftIris && rightIris) {
        // Iris position relative to eye bounds (0=left edge, 1=right edge)
        const leftIrisRatio = (leftIris.x - leftEyeInner.x) / (leftEyeOuter.x - leftEyeInner.x || 0.01)
        const rightIrisRatio = (rightIris.x - rightEyeInner.x) / (rightEyeOuter.x - rightEyeInner.x || 0.01)
        gazeX = (leftIrisRatio + rightIrisRatio) / 2 - 0.5  // centered at 0
        gazeY = ((leftIris.y + rightIris.y) / 2) - ((leftEyeInner.y + rightEyeInner.y) / 2)
      } else {
        // Fallback: nose-to-eye-center heuristic
        const nose = landmarks[1]
        const eyeCenterX = ((leftEyeInner?.x || 0) + (rightEyeInner?.x || 0)) / 2
        const eyeCenterY = ((leftEyeInner?.y || 0) + (rightEyeInner?.y || 0)) / 2
        gazeX = nose.x - eyeCenterX
        gazeY = nose.y - eyeCenterY
      }

      const isOffScreen = Math.abs(gazeX) > 0.12 || gazeY < -0.08 || gazeY > 0.15

      // Feature: gaze vector
      featuresRef.current.gaze_vectors.push({
        t: elapsed(),
        x: Math.round(gazeX * 1000) / 1000,
        y: Math.round(gazeY * 1000) / 1000,
        off_screen: isOffScreen,
      })

      // Feature: head pose estimation from face landmarks
      const chin = landmarks[152]
      const forehead = landmarks[10]
      const leftCheek = landmarks[234]
      const rightCheek = landmarks[454]
      if (chin && forehead && leftCheek && rightCheek) {
        // Pitch (nod): chin-to-forehead vertical ratio
        const faceHeight = Math.abs(forehead.y - chin.y) || 0.01
        const chinOffset = (chin.y - forehead.y) / faceHeight
        // Yaw (shake): cheek-to-cheek horizontal ratio
        const faceWidth = Math.abs(rightCheek.x - leftCheek.x) || 0.01
        const cheekOffset = (rightCheek.x - leftCheek.x) / faceWidth
        // Roll (tilt): eye angle
        const eyeAngle = Math.atan2(rightEyeOuter.y - leftEyeOuter.y, rightEyeOuter.x - leftEyeOuter.x)
        const roll = Math.round(eyeAngle * 100) / 100
        const pitch = Math.round((chinOffset - 0.5) * 100) / 100
        const yaw = Math.round((cheekOffset - 0.5) * 100) / 100
        featuresRef.current.head_pose.push({ t: elapsed(), pitch, yaw, roll })
      }

      if (isOffScreen) {
        if (!gazeAwaySinceRef.current) gazeAwaySinceRef.current = Date.now()
      } else {
        if (gazeAwaySinceRef.current) {
          const awayDuration = Date.now() - gazeAwaySinceRef.current
          if (awayDuration > GAZE_OFF_THRESHOLD_MS) {
            // Dedup: don't fire again within GAZE_DEDUP_WINDOW_MS of last gaze event
            const now = Date.now()
            if (now - lastGazeEventRef.current > GAZE_DEDUP_WINDOW_MS) {
              flagsRef.current.gaze_off_screen_count++
              addTimelineEvent('gaze_off_screen', { duration: Math.round(awayDuration / 1000) })
              lastGazeEventRef.current = now
            }
          }
          gazeAwaySinceRef.current = null
        }
      }
    } catch {
      // Face mesh not available — skip silently
    }
  }, [addTimelineEvent])

  // ── Tab / visibility detection (deduped) ─────────────────────────
  useEffect(() => {
    if (!active) return
    let lastSwitchTime = 0
    const onVisChange = () => {
      if (document.hidden) {
        const now = Date.now()
        if (now - lastSwitchTime > 1000) {
          flagsRef.current.tab_switch_count++
          addTimelineEvent('tab_switch')
          lastSwitchTime = now
        }
      }
    }
    const onBlur = () => {
      const now = Date.now()
      // Only count if not already counted by visibilitychange within 1s
      if (now - lastSwitchTime > 1000) {
        flagsRef.current.tab_switch_count++
        addTimelineEvent('window_blur')
        lastSwitchTime = now
      }
      lastBlurRef.current = now
    }
    document.addEventListener('visibilitychange', onVisChange)
    window.addEventListener('blur', onBlur)
    return () => {
      document.removeEventListener('visibilitychange', onVisChange)
      window.removeEventListener('blur', onBlur)
    }
  }, [active, addTimelineEvent])

  // ── Paste detection ──────────────────────────────────────────────
  useEffect(() => {
    if (!active) return
    const onPaste = (e) => {
      const text = e.clipboardData?.getData('text') || ''
      if (text.length > PASTE_SIZE_THRESHOLD) {
        flagsRef.current.paste_event_count++
        addTimelineEvent('paste_event', { length: text.length })
      }
    }
    document.addEventListener('paste', onPaste)
    return () => document.removeEventListener('paste', onPaste)
  }, [active, addTimelineEvent])

  // ── Right-click prevention ───────────────────────────────────────
  useEffect(() => {
    if (!active) return
    const onContext = (e) => {
      e.preventDefault()
      flagsRef.current.right_click_count++
      addTimelineEvent('right_click')
    }
    document.addEventListener('contextmenu', onContext)
    return () => document.removeEventListener('contextmenu', onContext)
  }, [active, addTimelineEvent])

  // ── DevTools detection heuristic ─────────────────────────────────
  useEffect(() => {
    if (!active) return
    let checking = false
    const check = () => {
      if (checking) return
      checking = true
      const threshold = 100
      const start = performance.now()
      debugger  // eslint-disable-line no-debugger
      const elapsed = performance.now() - start
      if (elapsed > threshold) {
        if (!flagsRef.current.devtools_opened) {
          flagsRef.current.devtools_opened = true
          addTimelineEvent('devtools_opened')
        }
      }
      checking = false
    }
    const interval = setInterval(check, 5000)
    return () => clearInterval(interval)
  }, [active, addTimelineEvent])

  // ── Typing speed (WPM) — counts ALL keystrokes ───────────────────
  useEffect(() => {
    if (!active) return
    const onKey = (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return
      if (e.key === 'Shift' || e.key === 'Control' || e.key === 'Alt' || e.key === 'Meta') return
      keystrokeCountRef.current++
      totalKeystrokesRef.current++
    }

    // Check WPM every 5 seconds based on ALL keystrokes
    wpmCheckTimerRef.current = setInterval(() => {
      const count = keystrokeCountRef.current
      keystrokeCountRef.current = 0
      if (count > 0) {
        // WPM = (characters typed / 5) / (time in minutes)
        // characters ≈ keystrokes (minus modifiers, already filtered)
        // time window = 5 seconds = 5/60 minutes
        const wpm = Math.round((count / 5) / (5 / 60))
        if (wpm > TYPING_SPEED_WPM_SUSPICIOUS) {
          flagsRef.current.code_typed_too_fast = true
          addTimelineEvent('typing_too_fast', { wpm, keystrokes: count })
        }
      }
    }, 5000)

    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('keydown', onKey)
      clearInterval(wpmCheckTimerRef.current)
    }
  }, [active, addTimelineEvent])

  // ── Audio voice activity with baseline calibration ───────────────
  const startAudioMonitoring = useCallback(async (stream) => {
    try {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)()
      const source = audioCtxRef.current.createMediaStreamSource(stream)
      analyserRef.current = audioCtxRef.current.createAnalyser()
      analyserRef.current.fftSize = 512
      source.connect(analyserRef.current)

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)

      // Phase 1: Baseline calibration — measure candidate's own voice level
      audioBaselineRef.current = { samples: [], candidateMaxEnergy: 0, calibrated: false }
      const baselineSamples = []

      audioTimerRef.current = setInterval(() => {
        if (!analyserRef.current) return
        analyserRef.current.getByteFrequencyData(dataArray)
        const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length / 255

        // Calibration phase (first 5 seconds)
        if (!audioBaselineRef.current.calibrated) {
          baselineSamples.push(avg)
          if (Date.now() - startTimeRef.current > VOICE_BASELINE_DURATION_MS) {
            // Set candidate's max energy as baseline (p95)
            const sorted = [...baselineSamples].sort((a, b) => a - b)
            audioBaselineRef.current.candidateMaxEnergy = sorted[Math.floor(sorted.length * 0.95)] || AUDIO_ENERGY_THRESHOLD
            audioBaselineRef.current.calibrated = true
            // Reset voice state after calibration
            voiceActiveRef.current = false
            voiceStartRef.current = null
          }
          return
        }

        // Phase 2: Active monitoring — detect voice ABOVE candidate's baseline
        const threshold = Math.max(audioBaselineRef.current.candidateMaxEnergy * 1.5, AUDIO_ENERGY_THRESHOLD)
        const isVoice = avg > threshold

        // Feature: audio energy + speech ratio
        if (featuresRef.current.audio_features.length === 0 ||
            elapsed() - featuresRef.current.audio_features[featuresRef.current.audio_features.length - 1].t >= 1) {
          // Compute spectral centroid proxy (higher = brighter/more speech-like)
          analyserRef.current.getByteFrequencyData(dataArray)
          let weightedSum = 0
          let totalEnergy = 0
          for (let i = 0; i < dataArray.length; i++) {
            weightedSum += i * dataArray[i]
            totalEnergy += dataArray[i]
          }
          const spectralCentroid = totalEnergy > 0 ? weightedSum / totalEnergy / dataArray.length : 0
          // Speech ratio: fraction of this second that had voice activity
          audioEnergyHistoryRef.current.push(isVoice ? 1 : 0)
          if (audioEnergyHistoryRef.current.length > 50) audioEnergyHistoryRef.current.shift()
          const speechRatio = audioEnergyHistoryRef.current.reduce((a, b) => a + b, 0) / audioEnergyHistoryRef.current.length

          featuresRef.current.audio_features.push({
            t: elapsed(),
            energy: Math.round(avg * 1000) / 1000,
            spectral_centroid: Math.round(spectralCentroid * 1000) / 1000,
            speech_ratio: Math.round(speechRatio * 100) / 100,
            is_speaking: isVoice,
          })
        }

        if (isVoice && !voiceActiveRef.current) {
          voiceActiveRef.current = true
          voiceStartRef.current = Date.now()
        } else if (!isVoice && voiceActiveRef.current) {
          voiceActiveRef.current = false
          const voiceDuration = Date.now() - voiceStartRef.current
          if (voiceDuration > 2000) {
            flagsRef.current.second_voice_count++
            addTimelineEvent('second_voice', { duration: Math.round(voiceDuration / 1000) })
          }
        }
      }, 200)
    } catch {
      // Audio not available — flag it
      flagsRef.current.camera_denied = true
    }
  }, [addTimelineEvent])

  // ── Integrity score computation ──────────────────────────────────
  const computeIntegrity = useCallback(() => {
    const f = flagsRef.current
    let deductions = 0
    deductions += Math.floor(f.face_absent_seconds / 10) * weights.face_absent_per_10s
    deductions += f.multiple_faces_count * weights.multiple_faces
    deductions += f.gaze_off_screen_count * weights.gaze_off_screen
    deductions += f.second_voice_count * weights.second_voice
    deductions += f.tab_switch_count * weights.tab_switch
    deductions += f.paste_event_count * weights.paste_event
    if (f.code_typed_too_fast) deductions += weights.code_typed_too_fast
    deductions += f.right_click_count * weights.right_click
    if (f.devtools_opened) deductions += weights.devtools
    return Math.max(0, 100 - deductions)
  }, [weights])

  // ── Start / stop lifecycle ───────────────────────────────────────
  const start = useCallback(async () => {
    if (!active) return
    startTimeRef.current = Date.now()
    lastFrameTimeRef.current = Date.now()
    timelineRef.current = []
    flagsRef.current = {
      face_absent_seconds: 0, multiple_faces_count: 0, gaze_off_screen_count: 0,
      second_voice_count: 0, tab_switch_count: 0, paste_event_count: 0,
      code_typed_too_fast: false, right_click_count: 0, devtools_opened: false,
      camera_denied: false,
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 }, audio: true })
      streamRef.current = stream
      const video = document.createElement('video')
      video.srcObject = stream
      video.muted = true
      video.playsInline = true
      await video.play()
      videoRef.current = video

      // Start face detection loop
      frameTimerRef.current = setInterval(() => {
        detectFace()
        detectGaze()
      }, FRAME_INTERVAL_MS)

      // Start audio monitoring
      startAudioMonitoring(stream)
    } catch {
      // Camera/mic denied — flag it so HR knows proctoring was degraded
      flagsRef.current.camera_denied = true
      addTimelineEvent('camera_denied')
    }
  }, [active, detectFace, detectGaze, startAudioMonitoring, addTimelineEvent])

  const stop = useCallback(() => {
    if (frameTimerRef.current) clearInterval(frameTimerRef.current)
    if (audioTimerRef.current) clearInterval(audioTimerRef.current)
    if (wpmCheckTimerRef.current) clearInterval(wpmCheckTimerRef.current)
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop())
      streamRef.current = null
    }
    if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
      audioCtxRef.current.close().catch(() => {})
    }
    // Flush pending gaze-away
    if (gazeAwaySinceRef.current) {
      const awayDuration = Date.now() - gazeAwaySinceRef.current
      if (awayDuration > GAZE_OFF_THRESHOLD_MS) {
        flagsRef.current.gaze_off_screen_count++
        addTimelineEvent('gaze_off_screen', { duration: Math.round(awayDuration / 1000) })
      }
      gazeAwaySinceRef.current = null
    }
    // Flush pending voice segment
    if (voiceActiveRef.current && voiceStartRef.current) {
      const voiceDuration = Date.now() - voiceStartRef.current
      if (voiceDuration > 2000) {
        flagsRef.current.second_voice_count++
        addTimelineEvent('second_voice', { duration: Math.round(voiceDuration / 1000) })
      }
    }
    videoRef.current = null
    mediaPipeDetectorRef.current = null
    mediaPipeLandmarkerRef.current = null
    audioBaselineRef.current = null
    voiceActiveRef.current = false
    voiceStartRef.current = null
    audioEnergyHistoryRef.current = []
    // Reset features for next session
    featuresRef.current = {
      face_landmarks: [], gaze_vectors: [], head_pose: [],
      audio_features: [], eye_contact_pct: 0, total_frames: 0,
    }
  }, [addTimelineEvent])

  const getProctoringData = useCallback(() => {
    // Compute eye contact percentage from gaze vectors
    const gazes = featuresRef.current.gaze_vectors
    const eyeContactFrames = gazes.filter((g) => !g.off_screen).length
    const eyeContactPct = gazes.length > 0 ? Math.round((eyeContactFrames / gazes.length) * 100) : 100
    featuresRef.current.eye_contact_pct = eyeContactPct

    // Compute non-verbal metrics from collected features
    const bboxes = featuresRef.current.face_landmarks.map((f) => f.bbox)
    let headMovement = 0
    for (let i = 1; i < bboxes.length; i++) {
      const dx = bboxes[i].x - bboxes[i - 1].x
      const dy = bboxes[i].y - bboxes[i - 1].y
      headMovement += Math.sqrt(dx * dx + dy * dy)
    }

    // Compute speech metrics
    const audioFeats = featuresRef.current.audio_features
    const avgEnergy = audioFeats.length > 0
      ? audioFeats.reduce((a, f) => a + f.energy, 0) / audioFeats.length
      : 0
    const avgSpeechRatio = audioFeats.length > 0
      ? audioFeats.reduce((a, f) => a + f.speech_ratio, 0) / audioFeats.length
      : 0

    // Stress proxy: high gaze aversion + high head movement + low speech ratio = stress
    const gazeAversionRate = 1 - (eyeContactPct / 100)
    const normalizedMovement = Math.min(headMovement / Math.max(bboxes.length, 1), 1)
    const stressScore = Math.round((gazeAversionRate * 40 + normalizedMovement * 30 + (1 - avgSpeechRatio) * 30))

    return {
      integrity_score: computeIntegrity(),
      flags: { ...flagsRef.current },
      timeline: timelineRef.current.filter((e) => e.event !== 'camera_denied'),
      duration_seconds: elapsed(),
      features: {
        face_landmarks: featuresRef.current.face_landmarks,
        gaze_vectors: featuresRef.current.gaze_vectors,
        head_pose: featuresRef.current.head_pose,
        audio_features: featuresRef.current.audio_features,
      },
      analysis: {
        nonverbal: {
          eye_contact_pct: eyeContactPct,
          head_movement_score: Math.round((1 - normalizedMovement) * 100),
          total_frames: featuresRef.current.total_frames,
        },
        speech: {
          avg_energy: Math.round(avgEnergy * 1000) / 1000,
          speech_ratio: Math.round(avgSpeechRatio * 100) / 100,
          avg_spectral_centroid: audioFeats.length > 0
            ? Math.round(audioFeats.reduce((a, f) => a + f.spectral_centroid, 0) / audioFeats.length * 1000) / 1000
            : 0,
        },
        confidence: {
          overall_score: Math.max(0, 100 - stressScore),
          gaze_aversion_rate: Math.round(gazeAversionRate * 100),
          head_movement_normalized: Math.round(normalizedMovement * 100),
        },
      },
    }
  }, [computeIntegrity, elapsed])

  // Cleanup on unmount
  useEffect(() => {
    return () => stop()
  }, [stop])

  return { start, stop, getProctoringData }
}
