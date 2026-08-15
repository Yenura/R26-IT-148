import urllib.request
import json

def login():
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/login/candidate',
        data=json.dumps({'email': 'candidate@example.com', 'password': 'Candidate@123'}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())['access_token']

token = login()

cv_text = """Inuka Jathmal
Email: inukajathmal11@gmail.com
Phone: +94 78 3730 114
Education: BSc (Hons) in Information Technology Specializing in Information Systems Engineering.
Experience: Software Engineering Intern (1 year)
Skills: Python, SQL, React, FastAPI, JavaScript, Git, HTML, CSS, MongoDB, PostgreSQL, Pandas
Certifications: AWS Certified Developer
Projects: E-commerce Web Application, Machine Learning Classifier
"""

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
lines = [
    f'--{boundary}',
    'Content-Disposition: form-data; name="file"; filename="Inuka_Jathmal_CV.txt"',
    'Content-Type: text/plain',
    '',
    cv_text,
    f'--{boundary}--',
    ''
]
body = '\r\n'.join(lines).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/resume/upload',
    data=body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': f'Bearer {token}'
    }
)
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())
print('Resume Uploaded Successfully!')
print('Resume ID:', data['id'])
print('Candidate Name:', data['candidate_name'])
print('Detected Skills:', data['skills'])

# Now test match endpoint
m_url = f"http://127.0.0.1:8000/api/v1/resume/match?resume_id={data['id']}&target_role=Data%20Scientist"
req_m = urllib.request.Request(m_url, headers={'Authorization': f'Bearer {token}'})
m_res = json.loads(urllib.request.urlopen(req_m).read().decode())
print('\nMatch Result for Data Scientist:')
print('Predicted Role:', m_res['predicted_role'])
print('Overall Score:', m_res['overall_score'])
print('Skill Score:', m_res['skill_score'])
print('Matched Skills:', m_res['matched_skills'])
print('Missing Skills:', m_res['missing_skills'])
