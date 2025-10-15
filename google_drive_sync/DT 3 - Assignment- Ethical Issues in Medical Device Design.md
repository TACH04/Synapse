DT 3 - Assignment: Ethical Issues in Medical Device Design
Project: AI/ML-Based Communications Trainer for Hospice Care
Team: Elijah Don, Tanner Hochberg, Alex Roussas, Ian Marcon, Ethan Vanderpool
Date: October 8, 2025


This submission contains a comprehensive analysis of the ethical considerations relating to our team's medical device design project. The analysis is broken down into six core components.


1. Ethical Framework Analysis
Our analysis of the ethical dimensions of the AI/ML Communications Trainer is grounded in two ethical frameworks: Utilitarianism and Deontology. The selection of these frameworks is justified because our project involves balancing the broad societal benefits of improved healthcare communication against the fundamental duties we owe to every individual involved.


Utilitarianism: The Greatest Good
Utilitarianism suggests that the most ethical action is the one that produces the greatest good for the greatest number of people. Engineering, as a discipline, often draws from this perspective.
* Application to Project: The primary goal of our trainer is to enhance the communication and empathy skills of medical practitioners, especially in the sensitive context of hospice care.
   * Benefits: Widespread adoption could lead to significantly improved end-of-life experiences for thousands of patients and their families, reducing emotional distress and preserving patient dignity. For practitioners, it offers a tool to build resilience and communication strategies, potentially lowering burnout rates associated with emotionally taxing conversations. This directly aligns with the goal of making human life better through technology.
   * Harms: A purely utilitarian view could risk overlooking harm to a minority. For instance, if the AI is trained on biased data, it might provide poor feedback to practitioners from underrepresented groups, harming their professional development. Likewise, a data breach, while affecting a small percentage of users, represents a significant harm. These are both risks that must be considered throughout the development of the project.
   * Conclusion: A utilitarian lens compels us to maximize the profound benefits of our tool while designing robust safeguards to mitigate potential harms like algorithmic bias and data insecurity, ensuring the net impact is overwhelmingly positive for society.


Deontology: Unconditional Duties
Deontology, particularly Kant's Categorical Imperative, focuses on unconditional moral duties. It has two key parts: acting according to rules that should be universal and, crucially, treating all people as ends in themselves, never merely as means to an end.
* Application to Project: This framework forces us to consider the inherent rights of every individual our project impacts.
   * Duty to Protect Privacy: Conversations about end-of-life care are personal. Using patient data to train our AI could be seen as using patients as a "means" to the "end" of training doctors. Our unconditional duty is to uphold the highest standards of privacy, which means implementing high-tech security and being transparent with users about how their data is handled. This includes full compliance with regulations like HIPAA.
   * Duty of Fairness: Our system must treat all users fairly and respectfully, avoiding discrimination. A deontological approach demands that our AI's feedback be free from bias, regardless of a user's race, gender, accent, or background. This is a moral obligation that cannot be compromised for the sake of a successful rollout or lower development cost.
   * Conclusion: Deontology provides useful moral guardrails. It ensures that in our pursuit of a greater good, we do not violate our fundamental obligations to respect the autonomy, privacy, and dignity of both the patients whose experiences inform the system and the practitioners who use it.


2. Triple Bottom Line Assessment
The Triple Bottom Line framework evaluates a project's value through three lenses: People, Planet, and Profit. This assessment clarifies our project's broader impact beyond its immediate function.


People (Social Impact)
The primary value of our project lies in its positive social impact on key stakeholders.
* Patients and Families: The ultimate beneficiaries are patients who will receive more empathetic, clear, and compassionate communication during one of life's most difficult periods. This improves their quality of life and respects their dignity.
* Healthcare Providers: The tool directly serves medical residents, trainees, and practitioners by providing a safe, repeatable space to practice and improve difficult conversations. This can increase confidence, reduce professional burnout, and enhance job satisfaction.
* Broader Society: By improving end-of-life communication, the project contributes to a healthier societal approach to death and dying and improves societal trust in healthcare. 


Planet (Environmental Impact)
As a software-as-a-service (SaaS) platform, our project's environmental footprint has the potential to be significantly smaller than that of a physical medical device.
* Energy Consumption: The main environmental impact stems from the electricity required to power the data centers hosting the AI and the end-user devices running the application. 
* Mitigation Strategy: To minimize this impact, we will attempt to partner with cloud service providers committed to using renewable energy sources. The application will be optimized for energy efficiency on various devices. Our commitment to sustainable development practices is a core ethical responsibility.


Profit (Economic Impact)
For the project to be sustainable and accessible, it must be economically viable while upholding ethical principles of access and equity.
* Economic Sustainability: The business model will likely be a subscription service for medical schools, hospitals, hospice organizations, clinics, and more. This provides the revenue needed for ongoing research, development, maintenance, and data security.
* Ethical Dimensions of Access: A key ethical challenge is ensuring the technology does not only benefit well-off institutions, thereby widening the healthcare gap. To address this, we will explore a tiered pricing model, offer grants, or develop a free, feature-limited version for institutions in under-resourced communities. This ensures the economic model serves the broader goal of improving health for all populations.


3. Stakeholder Analysis
We have identified the following key stakeholders for this assignment:
* Primary Stakeholders:
   * Medical Trainees/Practitioners which will be the direct users of the training platform.
   * Patients and their Families who will be the ultimate beneficiaries of improved communication.
* Secondary Stakeholders:
   * Healthcare Institutions like medical schools, hospitals, and hospice organizations that will purchase and implement the training.
   * Medical Educators and Mentors who use the tool as part of their curriculum and to guide trainees.
   * AI Developers and Researchers who build and maintain the technology.
* Tertiary Stakeholders:
   * Regulatory Bodies like university IRBs, HIPAA compliance officers.
   * Insurance companies and hospital systems concerned with quality of care metrics.
   * The Public in general potential future patients and a society that benefits from a more compassionate healthcare system.


Analysis of Competing Interests and Balancing Strategies
* Data Needs vs. Patient Privacy. The AI model's effectiveness depends on large, high quality datasets of real or realistic conversations. However, patients have the right to the privacy of their health information.
   * Balancing Strategy:
      1. Using synthetic data and generating realistic but artificial conversation data to train the core models, avoiding the use of personal health information.
      2. Rigorous anonymization where if any real data is used, all 18 HIPAA identifiers will be scrubbed using automated tools and human review.
      3. Federated learning explores architectures where the model can be trained on data locally within a hospital's secure environment, so sensitive data is never transferred.
* Cost-Effectiveness vs. Quality of Training. Healthcare institutions may desire a low cost, easy to implement solution. However, a superficial tool could encourage a type of robotic empathy and fail to teach genuine communication skills, ultimately harming patients.
   * Balancing Strategy: Our value proposition will focus on quality and efficacy. We will publish validation studies demonstrating the tool's effectiveness. By offering a modular design we can provide a cost effective entry point while making the highest quality training available.
* Scalability vs. Algorithmic Fairness. To scale quickly, there might be a temptation to use easily available but homogenous datasets. This would bake in biases against minority doctors and patients, violating our duty to avoid discrimination.
   * Balancing Strategy: We will make fairness a core technical requirement. This involves proactively curating a diverse training dataset representing a wide range of accents, dialects, and cultural communication styles. We will implement ongoing bias audits as a non-negotiable part of our development lifecycle.
   * 4. Design-Specific Ethical Considerations
Challenge 1: Algorithmic Bias and Fairness
An AI model is only as fair as the data it is trained on. If the training data overrepresents one demographic, the AI may unfairly penalize the communication styles of minority practitioners or fail to recognize the needs of diverse patients. This is a direct violation of the professional duty to treat all persons fairly.
Design Solution:
* Proactive Data Curation: We will invest significant resources in creating or sourcing a balanced and representative dataset. This includes collaborating with medical professionals from diverse backgrounds to vet and label data.
* Bias Detection and Mitigation: We will build fairness metrics directly into our model validation pipeline, continuously testing for performance disparities across demographic axes.
* Transparency: We will be transparent with institutional clients about the demographic composition of our training data and the model's known limitations, aligning with our duty to be honest in stating claims.


Challenge 2: Data Privacy and Security in an AI Context
The Problem: The sensitive nature of end of life conversations requires privacy protections beyond standard regulations. A data breach could expose deeply personal information, causing immense harm to trainees and any patients whose de-identified data was used. This relates to the core tenets of "do no harm" in medical ethics and “protecting the privacy of others” in engineering ethics.
Design Solution:
* Privacy Preserving Technologies: We will implement encryption for all data in transit and at rest. We will explore advanced techniques like differential privacy to add mathematical noise to data, making it impossible to identify individuals.
* Strict Access Control: A role based access control system will ensure that only authorized personnel can access sensitive data for maintenance or research, and all access will be logged and audited.
* User Control: Users will have clear, simple controls over their data and the ability to delete their account and associated data at any time.


Challenge 3: The Risk of Dehumanization
The Problem: A significant risk is that users may learn to game the AI rather than develop genuine empathy. This could lead to a generation of practitioners who are skilled at appearing empathetic but lack the underlying emotional connection, diminishing patient dignity.
Design Solution:
* Human trainer presence: The trainer will be explicitly positioned as a tool for reflection to be used alongside human mentorship, not as a replacement for it. We want to keep a human trainer involved for most of the process. The user interface will prompt users with reflective questions rather than just providing a score.
* Nuanced Feedback: The AI's feedback will focus on high level communication principles instead of prescribing specific phrases. This encourages authentic adaptation over robotic repetition.




5. Integration Plan
Strategy for Remaining Design Phases
* Fairness, privacy, and user trust are top-level system requirements, just as critical as functional performance.
* Prototyping & Development: Each development sprint will conclude with a mandatory ethical review where new features are assessed against our ethical principles and the IEEE and BMES codes of ethics. These reviews and their outcomes will be documented in our Design History File.
* Validation & Testing: Our testing protocol will go beyond technical verification.
   * Alpha Testing: We will recruit a diverse cohort of medical trainees to test the prototype. Feedback sessions will include specific questions about perceived bias, privacy comfort, and the tool's impact on their learning process.
   * Expert Review: We will have ethicists, hospice care experts, and communication coaches review the AI's feedback to ensure its pedagogical and ethical soundness.


Metrics for Evaluating Ethical Performance
* Fairness: We will use the Disparate Impact Ratio, comparing the average feedback scores across different user demographic groups. A ratio close to 1.0 indicates fairness.
* Privacy: We will conduct regular penetration tests and third-party security audits to verify the robustness of our data protection measures.
* User Trust: We will administer the Trust in Automation Scale via a user survey pre- and post-prototype testing to quantitatively measure changes in user trust.


Documentation in Design History File
Our DHF will include a dedicated ethical design section containing:
* Minutes from all Ethical Review meetings.
* Results of all fairness metric calculations and bias audits.
* Reports from security audits and penetration tests.
* Summaries of user feedback pertaining to ethical concerns.
* This signed ethical commitment document.


6. Team Ethical Commitment
As the design team for the AI/ML Communications Trainer, we hereby commit ourselves to the highest ethical and professional conduct as outlined in the IEEE Code of Ethics and the BMES Code of Ethics.
We recognize the profound importance of our technology in affecting the quality of life for patients and their families. We accept our personal obligation to our profession and the communities we serve by agreeing to:
1. Hold paramount the safety, health, and welfare of the public, which includes protecting the privacy and dignity of all users and patients.
2. Treat all persons fairly and with respect, actively working to eliminate bias from our algorithms and promote equity in our design.
3. Be honest and realistic in stating claims about our technology's capabilities, ensuring we clearly communicate its role as a supportive tool, not a replacement for human judgment.
4. Maintain and improve our technical competence, particularly in the fast-evolving areas of AI ethics, fairness, and security, to ensure our product is both effective and responsible.
5. Support our colleagues and co-workers in following this code, fostering a team culture where ethical concerns can be raised openly and without fear of retaliation.
Signatures:
Elijah Don
Tanner Hochberg
Alex Roussas
Ian Marcon
Ethan Vanderpool


Individual Reflections
* Elijah Don: "My personal commitment is to champion the principle of 'do no harm.' I will constantly ask how our design choices could inadvertently cause emotional or psychological harm to a trainee or patient and advocate for safeguards to prevent it."
* Tanner Hochberg: "As an engineer on this project, I feel a personal obligation to ensure our AI is free from bias. My focus will be on advocating for diverse datasets and rigorous fairness testing, because a tool meant to teach empathy must, itself, be fundamentally fair to all its users."
* Alex Roussas: "I am committed to upholding the privacy of others. I will focus on implementing the most robust security measures possible, recognizing that protecting the sensitive conversations this tool handles is a foundational requirement for building user trust."
* Ian Marcon: "My responsibility is to ensure we remain grounded in the real-world context of hospice care. I will continuously seek input from clinicians and patients to ensure our 'solution' genuinely solves their problem without creating new burdens."
* Ethan Vanderpool: "I will commit to being honest and realistic about our technology's limitations. It is my ethical duty to ensure we never overstate our AI's capabilities and always present it as a tool to augment, not replace, the irreplaceable human connection in medicine."