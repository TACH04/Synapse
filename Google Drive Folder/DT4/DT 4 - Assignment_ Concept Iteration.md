# **DT 4 \- Assignment: Concept Iteration**

Team 19  
Members: Tanner Hochberg, Elijah Don, Alex Roussas, Ian Marcon, Ethan Vanderpool  
Date: October 15, 2025

### **1\. Core Concept Selection**

After comprehensive discussions with clinicians, analysis of reports from Mayo Clinic mentors, and a review of external studies, our team has committed to a specific design direction. Based on our initial Concept Map, we have selected the **Post-Encounter Language and Speech Pattern Analysis Tool** as our core concept.

**Revised Concept:** An AI-powered tool for all medical practitioners (including trainees) that uses deep learning and LLMs to analyze audiovisual recordings of patient interactions after they have concluded. The tool provides concise, actionable feedback to help clinicians reflect on and develop their empathy and communication skills.

### **2\. Vertical Thinking: Osborn's Checklist**

#### **Adapt**

* **Adapt for Team Debriefs:** The AI's summary of a conversation could be used as a standardized starting point for team-based debriefing sessions, enabling the entire healthcare team to reflect on a patient interaction.  
* **Adapt for Patient Education:** A simplified version of the analysis could be adapted for patients, helping them understand their own communication patterns and prepare questions for their next appointment.  
* **Adapt for Billing/Coding:** The transcript analysis could be adapted to automatically identify and suggest relevant billing codes related to time spent on counseling or care options.

#### **Modify**

* **Modify Feedback Delivery:** Instead of a detailed report, modify the feedback into a 30-second audio summary that a clinician can listen to while walking between patient rooms.  
* **Modify the Scoring System:** Modify the feedback from a numerical score to a qualitative response that highlights 1-2 things that went well and 1-2 opportunities for improvement, reducing the feeling of being graded.  
* **Modify Focus:** Allow the clinician to modify the focus of the analysis for each encounter, e.g., "Analyze this conversation for my use of empathetic statements" or "Analyze for clarity in explaining the treatment plan."

#### **Magnify**

* **Magnify with Broader Analysis:** Expand the tool's capability to analyze a clinician's performance across encounters over a year, identifying long-term trends, burnout indicators, or improvements.  
* **Magnify with Patient Outcome Correlation:** Integrate with the EMR to correlate communication patterns with patient outcomes (medication adherence, patient satisfaction scores), providing evidence-based insights.  
* **Magnify Input Sources:** Allow clinicians to upload and analyze other communication forms, such as anonymized emails or portal messages to patients, for holistic feedback.

#### **Minify**

* **Minify to a "Key Moment" Extractor:** Simplify the tool to only extract and present the single most impactful emotional moment from the conversation and a brief analysis for high-impact, low-effort reflection.  
* **Minify to a Transcription-Only Tool:** Reduce the feature set to simply providing a highly accurate, narrated transcript of the conversation, allowing the clinician to perform their own reflection.  
* **Minify the Interface:** Instead of a full interface, deliver the feedback as a concise email or text message summary, making it accessible.

#### **Substitute**

* **Substitute User:** The primary user could be the medical educator instead of the clinician. The platform would provide educators with analytics to track the progress of their trainees.  
* **Substitute Audio for Text:** Allow clinicians who are uncomfortable with recording audio to instead submit their post-encounter clinical notes for analysis. The AI could then analyze the narrative for patient-centered language and empathy.  
* **Substitute Feedback for Prediction:** Instead of providing feedback, the tool could analyze the first few minutes of a conversation and predict the likely outcome.

#### **Rearrange**

* **Rearrange the Workflow:** The analysis is initiated by the patient, not the doctor. A patient could consent to have the conversation analyzed, and the feedback would be a shared resource for both parties.  
* **Reverse the Analysis:** Have the AI analyze the patient’s speech rather than the clinician’s. The analysis could search for signs of confusion, distress, or unasked questions, providing the clinician with insights into the patient's perspective.  
* **Transpose Cause and Effect:** Instead of the conversation causing the feedback, the feedback could be used to prepare for the conversation. The tool could analyze patient records to generate a simulated patient, and the clinician would record themselves talking through a difficult conversation before ever meeting the real patient, using the AI's feedback to prepare.

#### **Combine**

* **Combine with Scheduling Software:** Integrate with the hospital's scheduling software to automatically generate scheduling suggestions based on conversations.   
* **Combine with a Mentorship Program:** Create a platform where trainees can share their feedback reports with their mentors to facilitate more structured and evidence-based coaching sessions.  
* **Combine with a Peer Database:** Anonymize and collect key insights from all conversations across an institution, creating a database where clinicians can find examples of how peers effectively handled similar situations.

### **3\. Lateral Thinking**

#### **Delphi Method: Questions for Experts**

1. **(For a Medical Ethicist):** What is the ethical line between constructive feedback and performance surveillance, and how do we design for the first option?  
2. **(For a Palliative Care Physician):** For feedback to be useful in the 5 minutes between patients, what is the most important piece of information you would want to know about your conversation?  
3. **(For a Health Informatics/IT Specialist):** What is the most secure and user-friendly method for a clinician to access sensitive feedback on a mobile device between patient rooms?  
4. **(For a Machine Learning Engineer):** To ensure the model is fair, what is the best technical approach to mitigate bias against clinicians with non-native accents or diverse communication styles in an analysis model?  
5. **(For a Medical Education Director):** How can we design the feedback to encourage a growth mindset, rather than making trainees feel anxious or graded on their empathy?  
6. **(For a Psychologist Specializing in Burnout):** What specific vocal or nonvocal biomarkers or speech patterns in a conversation recording would be the most reliable indicators of long-term emotional fatigue or burnout?  
7. **(For a Patient Advocate):** How should we design the consent process for recording conversations to be clear and transparent for the patient, ensuring it feels like a partnership in improving care?  
8. **(For a UI/UX Designer in Healthcare):** What design choices are most effective for presenting conversational data in a simple, quickly digestible format for a busy clinician on a small screen?  
9. **(For a Health Policy Expert):** Could an institution's use of a tool like this to track and improve communication quality have implications on insurance and liability, either positive or negative?  
10. **(For a Sociolinguist):** How do we distinguish between interaction types, given that social rules and language practices vary across cultures?

#### **Other People's Perspectives: Stakeholder Analysis**

1. **Medical Student:** Views the tool as a private, low-risk learning aid. They value the ability to get immediate, objective feedback on their communication skills after a challenging patient encounter, which is a significant improvement over relying on memory for later review with a supervisor.  
2. **Attending Physician (Residency Supervisor):** Sees the platform as a powerful coaching tool that provides concrete data for mentorship. It allows them to move beyond generic advice to specific, evidence-based feedback tied to clear moments in conversation.  
3. **Mid-Career Clinician:** The primary concern is workflow efficiency. The tool is only valuable if its feedback is extremely concise and accessible in the few minutes between patients. A simple summary on a mobile device is useful, while a complex dashboard that requires a login is not compatible.  
4. **Patient:** The perspective is one of conditional support. They are generally open to having conversations recorded for quality improvement, provided the process is transparent, consent is explicitly given, and their data is secure. The ultimate measure of success is whether it leads to better communication in future visits.  
5. **Hospital Administrator:** Perceives the tool as a strategic asset for quality improvement. They are interested in its potential to address patient satisfaction metrics and its ability to provide data for tracking communication trends.  
6. **Hospital IT/Cybersecurity Expert:** Focuses on risk and compliance. While a post-encounter model is less risky than live streaming, their primary concerns are ensuring encryption of audio data and HIPAA-compliant, secure storage of all analysis and health information.  
7. **Medical Device Regulator (FDA):** Their perspective is on classification and risk. A retrospective educational tool that does not direct live patient care would likely be viewed as a lower-risk device, simplifying the regulatory pathway compared to a real-time diagnostic or treatment-directing tool.  
8. **Healthcare Insurance Provider:** Views this through a lens prioritizing financially beneficial care. They see potential in offering financial incentives to healthcare systems that adopt such tools, if a clear link can be established between improved communication metrics and better patient outcomes or reduced costs.  
9. **AI Developer:** The primary technical challenge identified is context. For the feedback to be accurate, the AI must be able to differentiate between various clinical scenarios. EMR integration for contextual data is seen as an essential requirement.  
10. **Clinical Researcher:** Views the platform as a source for a novel dataset on real-world clinical communication. This opens up new possibilities for conducting large-scale studies to link specific communication behaviors with clinical outcomes.

### **4\. Design Evolution**

The initial "Live Feedback AI Bot" concept has been retired. The exercises above have refined the **Post-Encounter Analysis Tool** from a simple idea into a more robust and user-centric platform.  
The evolved design has several key characteristics:

1. **Focus on Useful Feedback:** The core value proposition is no longer real-time intervention but **immediate, concise, post-encounter feedback**. The design prioritizes a mobile-first interface that delivers insights in under 30 seconds, fitting into the natural gaps in a clinician's day (*from Mid-Career Clinician perspective and Minify*).  
2. **Tiered Feedback Model:** The platform will offer different levels of feedback detail. The default is a quick summary, but users (especially trainees) can also read through and analyze an annotated transcript with detailed metrics, satisfying the needs of both experienced and learning practitioners (*from Modify and Substitute User*).  
3. **Emphasis on Privacy and User Control:** Recognizing the concerns of patients and IT, the design now prioritizes a clear, opt-in consent workflow for patients and gives clinicians full control over which conversations are recorded and analyzed. This moves away from surveillance to a voluntary professional development tool.   
4. **Platform Designed for Future Integration:** The concept is a standalone app/site that can be linked to other systems. While full, native EMR integration is beyond the scope of this project, the architecture will be designed with secure APIs in mind. This allows for future possibilities, such as linking out from the EMR to a specific analysis or connecting with mentorship platforms (*from Combine*).

This evolution transforms the project into a practical, clinician-focused platform that respects workflow constraints and directly supports a culture of reflective practice and continuous improvement.  
