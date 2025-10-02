# RubriCheck – AI-Powered Rubric Grading Assistant

RubriCheck is an innovative AI tool designed to automate and enhance the grading process for written assignments using customizable rubrics. By leveraging advanced natural language processing (NLP) models, RubriCheck evaluates student submissions against detailed rubric criteria, providing instant, transparent, and actionable feedback.

---

## 🚀 Features

- **Custom Rubric Input**: Upload or create detailed rubrics with multiple criteria and performance levels.
- **Automated Grading**: The AI analyzes submitted work and assigns scores based on rubric descriptions.
- **Actionable Feedback**: Get concise explanations and suggestions for improvement for each criterion.
- **User-Friendly Interface**: Simple web interface for uploading rubrics, assignments, and viewing results.
- **Privacy First**: All submissions are kept confidential and under user control.

---

## 🛠️ How It Works

1. **Upload Rubric**: Input a rubric in a structured format (JSON or via a form).
2. **Submit Assignment**: Upload or paste the student’s work.
3. **AI Evaluation**: The system uses advanced language models to assess the work against each rubric criterion.
4. **Results & Feedback**: Receive a detailed report with scores and improvement tips for each rubric item.

---

## 🎯 Target Users

- **Teachers**: Streamline grading, ensure consistency, and save time.
- **Students**: Self-assess assignments before submission and understand areas for improvement.

---

## 📦 Example Use Case

A teacher uploads a rubric for a persuasive essay and collects student submissions. RubriCheck grades each essay according to the rubric, providing both a score and comments for clarity, argument strength, and grammar. Students can review the AI’s feedback and revise their work before final submission.

---

## 🏗️ Tech Stack

- **Frontend**: React (or your preferred framework)
- **Backend**: Python (Flask or FastAPI)
- **AI/NLP**: OpenAI API (GPT-4) or HuggingFace Transformers
- **Database**: MongoDB or PostgreSQL (optional)

---

## ⚡ Getting Started

1. **Clone the repository**
    ```bash
    git clone https://github.com/YanwenWang1125/rubricheck.git
    cd rubricheck
    ```

2. **Install dependencies**
    - Backend:  
      ```bash
      pip install -r requirements.txt
      ```
    - Frontend:  
      ```bash
      cd frontend
      npm install
      ```

3. **Set up API keys**  
   - Obtain an API key from [OpenAI](https://platform.openai.com/account/api-keys) or your preferred provider.
   - Add your API key to the backend environment variables.

4. **Run the app**
    - Backend:  
      ```bash
      python app.py
      ```
    - Frontend:  
      ```bash
      npm start
      ```

---

## 📝 Rubric Format Example

```json
{
  "criteria": [
    {
      "name": "Clarity",
      "levels": {
        "Excellent": "Ideas are clearly and logically presented.",
        "Good": "Ideas are mostly clear with minor issues.",
        "Fair": "Some ideas are unclear or disorganized.",
        "Poor": "Ideas are confusing and hard to follow."
      }
    },
    {
      "name": "Grammar",
      "levels": {
        "Excellent": "No grammar or spelling errors.",
        "Good": "Minor grammar or spelling errors.",
        "Fair": "Several grammar issues.",
        "Poor": "Frequent grammar and spelling mistakes."
      }
    }
  ]
}
```



🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License.

🙌 Acknowledgements
OpenAI
HuggingFace
