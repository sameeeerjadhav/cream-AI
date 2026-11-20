# UdyamSathi User Questions (त्रैभाषिक प्रश्नसंग्रह)

These 10 authentic questions reflect real-world inquiries from micro and small entrepreneurs across Maharashtra (e.g., Kolhapur agro-processing, Solapur textiles, Pune precision manufacturing, Nashik cold storage).

To ensure true user accessibility for first-generation founders, every question is documented in **English**, **Marathi (मराठी)**, and **Hindi (हिंदी)**.

---

### Q1. New Manufacturing Enterprise Eligibility
* **Context**: A founder in Sangli establishing a spices and jaggery manufacturing unit with ₹15 Lakh capital.
* **English**: Am I eligible for PMEGP assistance if I am setting up a new manufacturing business in a semi-rural taluka?
* **मराठी (Marathi)**: मी सांगली ग्रामीण भागात नवीन मसाला व गूळ प्रक्रिया उद्योग सुरू करत असल्यास, मला PMEGP योजनेअंतर्गत अनुदान मिळू शकते का?
* **हिंदी (Hindi)**: क्या मैं ग्रामीण क्षेत्र में नया विनिर्माण (मैन्युफैक्चरिंग) व्यवसाय शुरू करने पर PMEGP योजना के तहत सब्सिडी और ऋण का पात्र हूँ?
* **Dataset Coverage**: **Covered**. Grounded in `scheme-pmegp` record and Bank of Maharashtra PMEGP guidelines.

---

### Q2. Service Enterprise Statutory Cap
* **Context**: An IT repair and diagnostic center in Aurangabad with ₹25 Lakh estimated budget.
* **English**: What is the maximum project cost permissible for a service-sector business under PMEGP and CMEGP?
* **मराठी (Marathi)**: PMEGP आणि CMEGP अंतर्गत सेवा क्षेत्रातील (सर्व्हिस) व्यवसायासाठी कमाल प्रकल्प खर्च मर्यादा (कॅप) किती आहे?
* **हिंदी (Hindi)**: PMEGP और CMEGP योजनाओं के तहत सेवा क्षेत्र के व्यवसाय के लिए अधिकतम अनुमत परियोजना लागत सीमा क्या है?
* **Dataset Coverage**: **Covered**. The service sector project cap is strictly statutory at ₹20 Lakh (Rs 20,00,000).

---

### Q3. Rural Subsidy Rates under CMEGP
* **Context**: An entrepreneur in rural Ahmednagar applying for CMEGP.
* **English**: What percentage of margin money subsidy is available under CMEGP for an applicant in a rural area?
* **मराठी (Marathi)**: ग्रामीण भागातील अर्जदारासाठी CMEGP योजनेअंतर्गत किती टक्के मार्जिन मनी अनुदान (सबसिडी) मिळते?
* **हिंदी (Hindi)**: ग्रामीण क्षेत्र के आवेदक के लिए CMEGP योजना के तहत कितने प्रतिशत मार्जिन मनी सब्सिडी उपलब्ध है?
* **Dataset Coverage**: **Covered**. General category: 25% rural; Special category: 35% rural.

---

### Q4. General Category Equity Contribution
* **Context**: A general-category graduate starting a plastic molding workshop in Thane.
* **English**: How much own contribution (promoter equity) is required from a general-category applicant under PMEGP?
* **मराठी (Marathi)**: PMEGP योजनेत सर्वसाधारण (General) प्रवर्गातील अर्जदाराला स्वतःचे किती टक्के भांडवल (Own Contribution) गुंतवावे लागते?
* **हिंदी (Hindi)**: PMEGP योजना में सामान्य वर्ग के उद्यमी को अपनी तरफ से कितने प्रतिशत स्वयं का अंशदान देना होता है?
* **Dataset Coverage**: **Covered**. General category requires 10% own equity; Special category requires 5%.

---

### Q5. Greenfield Enterprise for Women Entrepreneurs
* **Context**: A woman founder in Pune establishing an apparel production unit.
* **English**: Which scheme offers higher financial benefits for a woman entrepreneur launching a greenfield enterprise in Maharashtra?
* **मराठी (Marathi)**: महाराष्ट्रात नवीन उद्योग सुरू करणाऱ्या महिला उद्योजकांसाठी कोणती योजना अधिक फायदेशीर आहे आणि महिलांना विशेष प्रवर्गाचा लाभ मिळतो का?
* **हिंदी (Hindi)**: महाराष्ट्र में नया व्यवसाय शुरू करने वाली महिला उद्यमियों के लिए कौन सी योजना अधिक सब्सिडी और कम अंशदान का लाभ देती है?
* **Dataset Coverage**: **Covered**. Women are classified under Special Category across both schemes, qualifying for 25% (urban) / 35% (rural) subsidy and only 5% own contribution.

---

### Q6. Live Application & Disbursement Status ⚠️ (UNANSWERABLE GUARD)
* **Context**: An applicant wondering about the processing of their loan application submitted last month.
* **English**: Has my PMEGP loan application (Ref: MH-2026-98124) been approved by the bank, and when will the subsidy amount be disbursed?
* **मराठी (Marathi)**: माझा PMEGP अर्ज मंजूर झाला आहे का, आणि अनुदानाची रक्कम माझ्या बँक खात्यात कधी जमा होईल?
* **हिंदी (Hindi)**: क्या मेरा PMEGP ऋण आवेदन बैंक द्वारा स्वीकृत हो गया है, और सब्सिडी का पैसा कब खाते में आएगा?
* **Dataset Coverage**: **NOT IN DATASET (Defensive Refusal Guard)**.
  - *Reasoning*: UdyamSathi stores static policy documents, statutory project caps, and subsidy rules. It intentionally holds no access to live bank core systems, personal credit files, or nodal agency portal logins.
  - *Expected System Behavior*: Must return an explicit refusal: *"I don't know. UdyamSathi does not have access to live bank loan applications or individual disbursement statuses. Please check the official KVIC portal or your lending branch."*

---

### Q7. One-Family Assistance Rule
* **Context**: A family in Solapur where the husband already has an active PMEGP unit.
* **English**: Can two different members of the same family avail PMEGP financial assistance for separate businesses?
* **मराठी (Marathi)**: एकाच कुटुंबातील दोन वेगवेगळ्या व्यक्ती स्वतंत्र व्यवसायासाठी PMEGP योजनेचा लाभ घेऊ शकतात का?
* **हिंदी (Hindi)**: क्या एक ही परिवार के दो अलग-अलग सदस्य अलग-अलग व्यवसायों के लिए PMEGP योजना के तहत ऋण ले सकते हैं?
* **Dataset Coverage**: **Covered**. Stored in `rule-one-family`. Only one member per family (defined as self and spouse) is eligible.

---

### Q8. Educational Qualification Thresholds
* **Context**: An applicant in Satara with 7th standard education planning a ₹15 Lakh project.
* **English**: Is passing 8th standard mandatory for availing PMEGP or CMEGP assistance for projects exceeding ₹10 Lakh?
* **मराठी (Marathi)**: ₹10 लाखांपेक्षा जास्त खर्चाच्या प्रकल्पासाठी अर्जदाराचे किमान ८ वी किंवा १० वी पास असणे आवश्यक आहे का?
* **हिंदी (Hindi)**: क्या ₹10 लाख से अधिक की परियोजना लागत के लिए न्यूनतम 8वीं कक्षा उत्तीर्ण होना अनिवार्य है?
* **Dataset Coverage**: **Covered**. Stored in `rule-education-threshold`. Minimum 8th standard pass is mandatory for manufacturing projects above ₹10 Lakh and service projects above ₹5 Lakh.

---

### Q9. 2025 Revised MSME Classification Limits
* **Context**: A manufacturing unit owner checking if their investment exceeds the Micro enterprise limit.
* **English**: What are the latest 2025 investment in plant/machinery and annual turnover thresholds for a Micro enterprise?
* **मराठी (Marathi)**: सूक्ष्म (Micro) उद्योगासाठी २०२५ मधील संयंत्र/यंत्रसामग्रीतील गुंतवणूक आणि वार्षिक उलाढाल मर्यादा काय आहे?
* **हिंदी (Hindi)**: 2025 के नवीनतम मानदंडों के अनुसार सूक्ष्म (माइक्रो) उद्यम के लिए संयंत्र/मशीनरी में निवेश और वार्षिक टर्नओवर की सीमा क्या है?
* **Dataset Coverage**: **Covered**. Stored in `msme-micro-2025`. Investment up to ₹1 Crore and Turnover up to ₹5 Crore.

---

### Q10. MUDRA Scheme Integration for Tiny Food Units
* **Context**: A small roadside food packaging unit in Nagpur needing ₹5 Lakh equipment loan.
* **English**: Can a small food-processing venture obtain working capital support through Pradhan Mantri MUDRA Yojana alongside basic state schemes?
* **मराठी (Marathi)**: लहान अन्न प्रक्रिया किंवा गृहउद्योगासाठी मुद्रा (MUDRA - Shishu/Kishore) योजनेअंतर्गत कर्ज मिळू शकते का?
* **हिंदी (Hindi)**: क्या छोटे खाद्य प्रसंस्करण या टिफिन सेवा व्यवसाय के लिए मुद्रा (MUDRA) योजना के तहत ₹5 लाख तक का ऋण मिल सकता है?
* **Dataset Coverage**: **Covered**. Stored in `scheme-mudra`. MUDRA Kishore covers loans between ₹50,000 and ₹5,00,000 for non-corporate micro enterprises.
