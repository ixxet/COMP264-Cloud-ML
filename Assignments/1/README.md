# Assignment 1 – Interacting with Amazon Web Services

**Course:** COMP 264 – Cloud ML
**Weight:** Exercises weighted 25% / 25% / 50%
**Due:** Friday, Week 6
**Student:** Izzet Abidi (300898230)

---

## 1. Overview

This assignment introduces programmatic interaction with AWS services through three progressively complex exercises. It begins with basic S3 file operations using the Python SDK, moves to NLP entity extraction using the AWS CLI, and culminates in extending a serverless application with text-to-speech capabilities. Together, these exercises build the foundation for cloud-based AI service integration that Assignment 2 builds upon.

## 2. Exercise Breakdown

### Exercise 1: Files Upload (25%)

**Objective:** Upload a group of files to an S3 bucket using the boto3 Python SDK.

**What the script does:**
1. Parses command-line arguments for bucket name, optional prefix, and file list
2. Records the start time of the upload process
3. Iterates through each file, checks existence, and uploads to S3
4. Catches `ClientError` exceptions and logs failure details
5. Records end time and prints total upload duration

**File manifest:**

| File | Purpose |
|------|---------|
| `izzet_filesuplolad.py` | Main upload script with argparse, boto3, and error handling |
| `izzet1.txt` | Test file 1 for upload |
| `izzet2.txt` | Test file 2 for upload |
| `izzet3.txt` | Test file 3 for upload |

### Exercise 2: Entity Extraction (25%)

**Objective:** Compare entity extraction results from Amazon Comprehend and Amazon Comprehend Medical on the same text input.

**What the script does:**
1. Accepts a text string containing personal information as input
2. Runs `aws iam get-user` to verify AWS identity and saves the output
3. Passes the text to `aws comprehend detect-entities` and saves extracted entities as JSON
4. Passes the same text to `aws comprehendmedical detect-phi` for PHI detection and saves as JSON

**File manifest:**

| File | Purpose |
|------|---------|
| `assignment1_ex2_commands.sh` | Bash script with all three AWS CLI commands |

**Output files (generated on execution):**
- `izzet_iam_get_user.json`
- `izzet_comprehend_output.json`
- `izzet_comprehend_medical_output.json`

### Exercise 3: Speaking Pictorial Translator (50%)

**Objective:** Extend the pictorial translator application to read translated text aloud using Amazon Polly.

**What the application does:**
1. Accepts an uploaded image via the `POST /images` endpoint
2. Stores the image in S3 using the storage service
3. Detects text in the image using Amazon Rekognition (filtered at 80% confidence)
4. Translates detected text using Amazon Translate
5. Synthesizes translated text into speech using Amazon Polly (neural engine)
6. Uploads the generated MP3 audio to S3
7. Returns the audio URL for playback in the HTML5 frontend

**Design decisions:**
- **Service-layer separation:** Each AWS service is wrapped in its own module (`storage_service.py`, `recognition_service.py`, `translation_service.py`, `speech_service.py`) for clean architecture and testability
- **Confidence filtering:** Only text detections with >= 80% confidence pass through to translation, reducing noisy OCR output
- **S3 for audio storage:** Reusing S3 for both images and generated audio simplifies the retrieval flow
- **Backward compatibility:** The new `/speak-text` endpoint preserves the existing `/translate-text` endpoint unchanged

**File manifest:**

| File | Purpose |
|------|---------|
| `izzet_speaking_pictorial/app.py` | Chalice REST API with all endpoints |
| `izzet_speaking_pictorial/requirements.txt` | Python dependencies |
| `izzet_speaking_pictorial/.chalice/config.json` | Chalice configuration with bucket env var |
| `izzet_speaking_pictorial/chalicelib/storage_service.py` | S3 upload wrapper |
| `izzet_speaking_pictorial/chalicelib/recognition_service.py` | Rekognition text detection wrapper |
| `izzet_speaking_pictorial/chalicelib/translation_service.py` | Amazon Translate wrapper |
| `izzet_speaking_pictorial/chalicelib/speech_service.py` | Amazon Polly TTS with S3 upload |
| `izzet_speaking_pictorial/frontend/index.html` | Web interface with file upload and audio player |
| `izzet_speaking_pictorial/frontend/scripts.js` | Frontend logic calling API endpoints |
| `diagrams/architecture.mmd` | Mermaid architecture diagram |
| `diagrams/component_interaction.mmd` | Mermaid component interaction diagram |

## 3. Runbook

### Prerequisites

```bash
pip install boto3 chalice
aws configure  # set region to ca-central-1
```

### Exercise 1

```bash
cd Assignments/1
python3 izzet_filesuplolad.py --bucket <your-bucket-name>
```

### Exercise 2

```bash
cd Assignments/1
chmod +x assignment1_ex2_commands.sh
./assignment1_ex2_commands.sh "Izzet Abidi izzet@example.com (416) 111-2222 123 Main St Toronto ON Centennial College"
```

### Exercise 3

```bash
cd Assignments/1/izzet_speaking_pictorial
chalice local
# open frontend/index.html in a browser
# API runs at http://127.0.0.1:8000
```

### Cleanup

```bash
# remove uploaded files from S3 after testing
aws s3 rm s3://<bucket-name>/izzet1.txt
aws s3 rm s3://<bucket-name>/izzet2.txt
aws s3 rm s3://<bucket-name>/izzet3.txt
# remove images and audio files from the speaking pictorial bucket
```

## 4. Expected Results

**Exercise 1:**
- Terminal shows each file name as upload starts, followed by confirmation
- S3 console shows all three `.txt` files in the specified bucket
- Total duration printed (typically < 5 seconds for small text files)

**Exercise 2:**
- `izzet_iam_get_user.json` contains IAM user details (ARN, user ID, creation date)
- `izzet_comprehend_output.json` contains entities with types like PERSON, EMAIL, PHONE, ADDRESS, ORGANIZATION
- `izzet_comprehend_medical_output.json` contains PHI entities with types like NAME, EMAIL, PHONE_OR_FAX, ADDRESS

**Exercise 3:**
- Uploading an image with foreign text returns detected text in the response
- Translation endpoint returns English text with source language identified
- Speak endpoint returns an audio URL; clicking play produces spoken English audio
- MP3 file is accessible via the returned S3 URL

## 5. Topics Learned

**Cloud Storage**
- S3 bucket operations — programmatic file upload using boto3
- Error handling — catching and logging AWS ClientError exceptions
- CLI output redirection — saving JSON API responses to files

**Natural Language Processing**
- Entity extraction — identifying named entities (persons, locations, organizations) in text
- PHI detection — recognizing protected health information using specialized medical NLP
- Service comparison — understanding when to use general vs. domain-specific NLP services

**Computer Vision and Translation**
- Text detection — extracting text from images using Amazon Rekognition
- Confidence filtering — using probability thresholds to control detection quality
- Machine translation — converting text between languages with Amazon Translate

**Speech Synthesis**
- Text-to-speech — generating natural speech audio using Amazon Polly's neural engine
- Audio format handling — working with MP3 streams and HTML5 audio playback
- Voice configuration — selecting voice IDs for different languages and styles

**Serverless Architecture**
- AWS Chalice — building REST APIs deployed as Lambda functions
- Service-oriented design — wrapping each AWS service in a dedicated module
- Frontend-backend integration — connecting browser-based UI to serverless endpoints

## 6. Definitions and Key Concepts

| Term | Definition |
|------|-----------|
| Amazon S3 | Simple Storage Service; object storage for files, data, and artifacts |
| boto3 | The official AWS SDK for Python, providing programmatic access to AWS services |
| ClientError | A botocore exception raised when an AWS API call fails |
| AWS CLI | Command-line interface for interacting with AWS services |
| Amazon Comprehend | Managed NLP service for entity extraction, sentiment analysis, and key phrases |
| Amazon Comprehend Medical | Specialized NLP service for extracting medical entities and PHI from text |
| Protected Health Information (PHI) | Personally identifiable health data regulated under HIPAA |
| Entity Extraction | Identifying and classifying named entities (person, location, date) in text |
| Amazon Rekognition | Computer vision service for image and video analysis |
| Text Detection | Recognizing and extracting printed text from images |
| Confidence Score | Probability value indicating how certain a detection or prediction is |
| Amazon Translate | Neural machine translation service supporting 70+ languages |
| Amazon Polly | Text-to-speech service that converts text into lifelike speech |
| Neural TTS Engine | Polly's advanced engine producing more natural-sounding speech |
| Voice ID | Identifier for a specific Polly voice (e.g., "Joanna" for US English) |
| AWS Chalice | Python serverless microframework for building REST APIs on AWS Lambda |
| CORS | Cross-Origin Resource Sharing; HTTP headers allowing browser cross-domain requests |
| REST API | Architectural style for web services using HTTP methods (GET, POST, PUT, DELETE) |
| Base64 Encoding | Binary-to-text encoding used to transmit image data in JSON payloads |
| Mermaid | Markdown-based diagramming language for architecture and flow diagrams |
| IAM | Identity and Access Management; AWS service for user and role permissions |
| pipenv | Python virtual environment and dependency management tool |

## 7. Potential Improvements and Industry Considerations

### Approach Comparison

| Category | Assignment Approach | Industry Alternative | Trade-Off |
|----------|-------------------|---------------------|-----------|
| File Upload | Sequential loop with boto3 | Multipart parallel upload with `s3 transfer` | Sequential is simple and debuggable; parallel is faster for large files |
| Error Handling | Catch ClientError, log, continue | Exponential backoff with retry decorator | Simple catch is readable; retry handles transient network failures |
| NLP Pipeline | Single API call per service | Batch processing with Comprehend batch jobs | Single call is instant for demo text; batch scales to thousands of documents |
| Image Text Detection | Rekognition DetectText | AWS Textract for structured document extraction | DetectText handles photos; Textract handles forms and tables |
| Translation | Auto-detect source language | User-selectable source language with validation | Auto-detect is convenient; explicit selection avoids misdetection |
| TTS Output | Single MP3 file in S3 | Streaming audio via WebSocket for low latency | File-based is simple to implement; streaming suits real-time applications |
| Deployment | `chalice local` for development | `chalice deploy` to AWS Lambda + API Gateway | Local is free and immediate; deployed is production-accessible |

### Where the Baseline Still Holds Up

- **Sequential file upload** is the correct choice for three small text files. The overhead of configuring parallel transfers would exceed the time saved. The simplicity also makes the code easier to explain in the demo video.
- **80% confidence threshold** for text detection is a reasonable default. Lowering it risks passing OCR noise to translation; raising it risks missing valid text. The chosen threshold balances precision and recall for typical image inputs.
- **Chalice local development** is appropriate for an assignment that demonstrates service integration. Deploying to Lambda would add IAM complexity and potential charges without improving the learning outcome.
