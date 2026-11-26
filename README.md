# DeepFake AI 🔍

## An AI-powered image detection system designed to identify AI-generated and manipulated images

### About the Project

DeepFake AI is a web-based application that aims to help users distinguish between authentic and potentially manipulated or AI-generated images.

Users can upload an image and receive an analysis result through an AI-based detection model.

The project focuses on making image verification simple, accessible and user-friendly.

## Steps to Run

 Create a pyton enviroment within `Backend/`.

```sh
python -m venv .venv
```

 Source the enviroment.

```sh
source .venv/bin/activate
```

 Install the required libraries.

```sh
pip install -r requirements.txt
```

 Run application with Uvicorn.

```sh
uvicorn main:app
```
The page can be viewed at `http://127.0.0.1:8000/` by default, can be changed with flags.
