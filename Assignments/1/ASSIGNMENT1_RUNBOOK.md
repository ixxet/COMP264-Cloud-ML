# Assignment 1 Runbook (Izzet)

## Exercise 1
```bash
cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Assignments/1"
python3 izzet_filesuplolad.py --bucket my-unique-bucket-20250118-xyz
```

## Exercise 2
```bash
cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Assignments/1"
./assignment1_ex2_commands.sh "Izzet Abidi izzet@my.centennialcollege.ca (416) 222 3441 233 Hoey crescent M3E1R7 Toronto Ontario Centennial College"
```

## Exercise 3 (local)
```bash
cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Assignments/1/izzet_speaking_pictorial"
# Use your existing venv where chalice+boto3 are installed
chalice local
```

Open frontend file:
- `/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Assignments/1/izzet_speaking_pictorial/frontend/index.html`

## Required screenshots/evidence
- Ex1 script run output + S3 console objects
- Ex2 command output and generated JSON files
- Ex3 API run and frontend/audio working
- Architecture + interaction diagrams in report

## Cleanup (avoid charges)
```bash
aws s3 rm s3://my-unique-bucket-20250118-xyz --recursive
```
