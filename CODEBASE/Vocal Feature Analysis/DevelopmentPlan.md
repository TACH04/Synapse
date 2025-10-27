Title: Development Plan: Vocal Features Analysis Module
Project: AI-Based Communication Trainer for Medical Professionals
Date: October 26, 2025
Version: 1.0

**Overall Goal:** Develop a robust module that takes raw audio from a recorded patient-practitioner conversation, analyzes vocal features indicative of emotion and communication style (e.g., empathy, stress), and outputs structured data for integration with a larger LLM-based feedback system.

**Approach:** Hybrid Feature Engineering + Deep Learning Fine-tuning. We will combine interpretable, engineered acoustic/prosodic features with powerful, learned features from a pre-trained deep learning model.

---

**Phase 1: Setup, Data Curation & Feature Research (Weeks 1-3: Approx. Oct 27 - Nov 14, 2025)**

* **Task 1.1: Environment Setup**
    * **Description:** Set up the Python development environment, install core libraries (`librosa`, `parselmouth-praat`, `numpy`, `pandas`, `scipy`, `soundfile`). Set up version control (Git) if not already done.
    * **Owner:** [Assign Team Member - e.g., Elijah Don]
    * **Deliverable:** Functional development environment, requirements.txt file.
    * **Best Option:** Standard Python environment using `venv` or `conda`.
* **Task 1.2: Data Acquisition & Preparation**
    * **Description:** Finalize and acquire datasets. Standardize audio formats (e.g., WAV, 16kHz mono). Establish data cleaning and preprocessing pipeline (noise reduction if necessary, silence removal).
    * **Owner:** [Assign Team Member - e.g., Ethan Vanderpool]
    * **Deliverable:** Organized collection of standardized audio files (Public datasets like RAVDESS, IEMOCAP; Mayo Clinic Sim Center data if available; AI-generated conversation audio).
    * **Best Option:** Prioritize Mayo Clinic data for relevance, supplement with public/AI data for volume and diversity. Ensure ethical approval/consent for Mayo data.
* **Task 1.3: Literature Review & Feature Selection**
    * **Description:** Deep dive into research identifying *which specific* vocal features (prosodic, spectral, voice quality) are most strongly correlated with target states (empathy, stress, anxiety, confidence, etc.) in *clinical* contexts. Refine the list of features to extract.
    * **Owner:** [Assign Team Member - e.g., Alex Roussas]
    * **Deliverable:** Document summarizing key research findings and the final list of engineered features to target.
    * **Best Option:** Focus on peer-reviewed studies in medical communication, psychology, and speech processing.

---

**Phase 2: Feature Extraction Pipeline Development (Weeks 4-6: Approx. Nov 17 - Dec 5, 2025)**

* **Task 2.1: Engineered Feature Extraction Script**
    * **Description:** Develop a Python script using `librosa` and `parselmouth` to extract the selected engineered features (e.g., MFCCs, pitch mean/std dev, jitter, shimmer, HNR, speaking rate) from audio segments. Handle potential errors gracefully (e.g., unable to extract pitch).
    * **Owner:** [Assign Team Member - e.g., Elijah Don]
    * **Deliverable:** Python script `extract_engineered_features.py`.
    * **Best Option:** Utilize functions proven effective in SER tasks within these libraries.
* **Task 2.2: Learned Feature Extraction Setup**
    * **Description:** Set up code using Hugging Face's `transformers` library to load a pre-trained, state-of-the-art speech model (e.g., `wav2vec 2.0` base or large) and extract hidden-state embeddings from raw audio segments.
    * **Owner:** [Assign Team Member - e.g., Tanner Hochberg]
    * **Deliverable:** Python script `extract_learned_features.py`.
    * **Best Option:** Start with `wav2vec2-base-960h`. Ensure compatibility with audio format.
* **Task 2.3: Feature Combination & Data Formatting**
    * **Description:** Create a script that orchestrates 2.1 and 2.2. For each audio segment, combine the engineered feature vector and the learned feature embedding (e.g., by concatenation or averaging pooling of learned features). Save these combined feature vectors along with their corresponding emotion/state labels (from dataset annotations) in a format suitable for model training (e.g., NumPy arrays, Pandas DataFrame, Hugging Face `Dataset` object).
    * **Owner:** [Assign Team Member - e.g., Tanner Hochberg]
    * **Deliverable:** Script `create_feature_dataset.py`, processed feature datasets.

---

**Phase 3: Model Training & Evaluation (Weeks 7-11: Approx. Dec 8, 2025 - Jan 16, 2026)**

* **Task 3.1: Base Model Selection & Setup**
    * **Description:** Choose a suitable classification head architecture to place on top of the feature extraction pipeline (e.g., a simple feed-forward network, or fine-tuning a sequence classification head if using `transformers`). Set up the training framework (e.g., PyTorch with `SpeechBrain` or `transformers.Trainer`). Define loss function (e.g., CrossEntropyLoss) and evaluation metrics (Accuracy, F1-Score, potentially metrics sensitive to class imbalance like weighted F1 or AUC).
    * **Owner:** [Assign Team Member - e.g., Elijah Don]
    * **Deliverable:** Training script structure, model architecture definition.
    * **Best Option:** Leverage `SpeechBrain` or `transformers.Trainer` for streamlined training loops, checkpointing, and evaluation.
* **Task 3.2: Initial Training on Public Datasets**
    * **Description:** Train the model using the combined features extracted from public datasets (RAVDESS, IEMOCAP). Tune hyperparameters (learning rate, batch size, epochs). Establish baseline performance.
    * **Owner:** [Assign Team Member - e.g., Alex Roussas]
    * **Deliverable:** Trained model checkpoint (baseline), initial performance report.
* **Task 3.3: Fine-tuning on Medical Data**
    * **Description:** Apply transfer learning. Fine-tune the model (trained in 3.2) using the combined features extracted from the curated medical conversation data (Mayo/AI-generated). Adjust hyperparameters for fine-tuning.
    * **Owner:** [Assign Team Member - e.g., Alex Roussas]
    * **Deliverable:** Fine-tuned model checkpoint (specialized), final performance report including confusion matrix and per-class metrics.
    * **Best Option:** Use techniques like gradual unfreezing or lower learning rates for fine-tuning to preserve knowledge from the base model while adapting to the target domain.
* **Task 3.4: Interpretability Analysis (Optional but Recommended)**
    * **Description:** If time permits, use techniques like SHAP or LIME, or analyze feature importance, to understand which features (engineered or learned components) contribute most to the model's predictions for different emotions/states.
    * **Owner:** [Assign Team Member - e.g., Ethan Vanderpool]
    * **Deliverable:** Brief report on feature importance/model interpretability.

---

**Phase 4: API Development & Integration Prep (Weeks 12-14: Approx. Jan 19 - Jan 30, 2026)**

* **Task 4.1: Develop Prediction API**
    * **Description:** Wrap the trained model (checkpoint from 3.3) and the full feature extraction pipeline (from Phase 2) into a simple API (e.g., using Flask/FastAPI). The API should accept a raw audio file path or audio data, perform feature extraction and prediction, and return the structured JSON output.
    * **Owner:** [Assign Team Member - e.g., Elijah Don]
    * **Deliverable:** Functional API endpoint, basic API documentation (input/output specs).
    * **Best Option:** FastAPI often offers better performance and automatic documentation generation.
* **Task 4.2: Define Final JSON Output**
    * **Description:** Finalize the precise structure of the JSON output based on the needs of the downstream LLM module. Ensure it includes emotion label, confidence score, start/end timestamps, and potentially key contributing features if interpretability is implemented.
    * **Owner:** [Assign Team Member - e.g., Tanner Hochberg]
    * **Deliverable:** Finalized JSON schema documentation.
* **Task 4.3: Containerization (Optional but Recommended)**
    * **Description:** Package the API and its dependencies into a Docker container for easier deployment and integration testing.
    * **Owner:** [Assign Team Member - e.g., Ian Marcon]
    * **Deliverable:** Dockerfile.

---

**Phase 5: Integration Testing & Handover (Weeks 15-16: Approx. Feb 2 - Feb 13, 2026)**

* **Task 5.1: Integration Testing**
    * **Description:** Work with the team members responsible for the diarization module and the LLM feedback module to test the end-to-end pipeline using sample conversations. Debug API calls and data flow.
    * **Owner:** All Team Members involved in integration.
    * **Deliverable:** Successful end-to-end processing of test audio files.
* **Task 5.2: Documentation & Knowledge Transfer**
    * **Description:** Finalize documentation for the Vocal Features module, including setup instructions, API usage, model performance details, and limitations. Ensure knowledge is transferred within the team.
    * **Owner:** [Assign Team Member - e.g., Ian Marcon]
    * **Deliverable:** Comprehensive module documentation.

---

**Key Technologies:** Python, Librosa, Parselmouth, Hugging Face Transformers (for wav2vec 2.0/HuBERT), SpeechBrain/PyTorch (for training), Flask/FastAPI (for API), Docker (optional).

**Success Metrics:**

* Achieve target F1-score/accuracy on the medical conversation test set.
* API successfully integrates with other system modules.
* Clear documentation delivered.

**Risks & Mitigation:**

* **Data Scarcity/Quality:** Mitigate by leveraging AI generation and public datasets; prioritize securing Mayo data.
* **Model Performance:** Mitigate by using SOTA pre-trained models, careful fine-tuning, and robust evaluation.
* **Integration Challenges:** Mitigate by defining clear API contracts early (Task 4.2) and conducting integration tests (Task 5.1).
* **Computational Resources:** Mitigate by utilizing available resources (e.g., ASU supercomputing as mentioned previously) and choosing appropriately sized models (e.g., `wav2vec2-base` vs `large`).