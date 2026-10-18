import { describe, it, expect } from 'vitest'
import { toArr, isValidEmail, avatarSrc } from './utils.js'

describe('toArr', () => {
  it('passes arrays through', () => {
    expect(toArr({ data: [1, 2] })).toEqual([1, 2])
  })
  it('unwraps nested data', () => {
    expect(toArr({ data: { data: [1] } })).toEqual([1])
  })
  it('unwraps named collections', () => {
    expect(toArr({ data: { resumes: [{ id: 1 }] } })).toEqual([{ id: 1 }])
    expect(toArr({ data: { jobs: [{ id: 2 }] } })).toEqual([{ id: 2 }])
  })
  it('returns [] for junk', () => {
    expect(toArr(null)).toEqual([])
    expect(toArr({})).toEqual([])
    expect(toArr({ data: 'nope' })).toEqual([])
  })
})

describe('isValidEmail (mirrors server check_email_format)', () => {
  it.each([
    'candidate@demo.com',
    'user.name+tag@sub.domain.co',
    'a@b.cd',
  ])('accepts %s', (v) => expect(isValidEmail(v)).toBe(true))

  it.each([
    '',
    'plainaddress',
    '@nodomain.com',
    'a@b.c',
    'bad..dots@gmail.com',
    '.lead@gmail.com',
    'trail.@gmail.com',
    'user@.com',
    'user@com.',
    'user@-bad.com',
    `${'x'.repeat(250)}@gmail.com`,
  ])('rejects %s', (v) => expect(isValidEmail(v)).toBe(false))
})

describe('avatarSrc', () => {
  it('passes absolute http(s) URLs through', () => {
    expect(avatarSrc('https://cdn.example.com/a.png')).toBe('https://cdn.example.com/a.png')
  })
  it('prefixes backend-relative paths with the API origin', () => {
    expect(avatarSrc('/api/v1/auth/avatar/123')).toBe('http://127.0.0.1:8000/api/v1/auth/avatar/123')
  })
  it('rejects empty, relative, and dangerous schemes', () => {
    expect(avatarSrc('')).toBe('')
    expect(avatarSrc('avatar.png')).toBe('')
    expect(avatarSrc('javascript:alert(1)')).toBe('')
    expect(avatarSrc('data:text/html,<h1>x</h1>')).toBe('')
  })
})
