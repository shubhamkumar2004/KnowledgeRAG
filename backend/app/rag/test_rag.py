import time

from app.rag.generator import generate_answer
from app.services.memory import create_session


TEST_SECTIONS = {

    # ==========================================================
    # ABOUT EKTA TRUST
    # ==========================================================

    "ABOUT EKTA TRUST": [

        "What insurance schemes are available?",
        "RSBY?",
        "UHIS?",
        "What is the vision of Ekta Trust?",
        "What is the motto of Ekta Trust?",
        "What are the objectives of Ekta Trust?",
        "What kind of society does Ekta Trust want to create?",
        "Who founded Ekta Trust?",
        "When was Ekta Trust established?",
        "How can I contact Ekta Trust?",
        "Where is Ekta Trust located?"
    ],

    # ==========================================================
    # JOIN / VOLUNTEER
    # ==========================================================

    "JOIN / VOLUNTEER": [

        "How can I join Ekta Trust?",
        "How can I volunteer with Ekta Trust?",
        "What information is required for joining?",
        "Is there any registration process?"
    ],

    # ==========================================================
    # DONATIONS
    # ==========================================================

    "DONATIONS": [

        "How can I donate?",
        "Is my donation tax exempt?",
        "Does Ekta Trust have 80G registration?",
        "Does Ekta Trust have 12A registration?"
    ],

    # ==========================================================
    # TRAINING
    # ==========================================================

    "TRAINING": [

        "What training programs are available?",
        "Is tailoring training available?",
        "Is driving training available?",
        "Is cooking training available?",
        "Is yoga training available?",
        "Is dairy training available?",
        "Is there any stipend for trainees?"
    ],

    # ==========================================================
    # EDUCATION LOAN (Conversation Test)
    # ==========================================================

    "EDUCATION LOAN": [

        "Tell me about the Education Loan Scheme.",
        "What is the maximum amount?",
        "Is collateral required?",
        "What is the interest rate?",
        "Who is eligible?",
        "Is there any margin requirement?"
    ],

    # ==========================================================
    # INSURANCE
    # ==========================================================

    "INSURANCE": [

        "What insurance schemes are mentioned?",
        "Does the website mention RSBY?",
        "What is UHIS?",
        "Does Ekta Trust provide insurance?"
    ],

    # ==========================================================
    # RUN FOR EQUALITY
    # ==========================================================

    "RUN FOR EQUALITY": [

        "What is Run for Equality?",
        "Where is the run route?",
        "What is the total distance?",
        "What is the SOP for participants?",
        "Can I see last year's winners?",
        "Is there a theme song?",
        "Can I view the gallery?",
        "Have any celebrities appealed for the event?",
        "Where is the Bib Expo?"
    ],

    # ==========================================================
    # MOCK INTERVIEW PROGRAMME
    # ==========================================================

    "MIP": [

        "What is the RPSC Mock Interview Programme?",
        "How do I register for the MIP?",
        "What documents are required?",
        "Is there any registration fee?",
        "Who can apply?",
        "Can I become a mentor?",
        "Who is the SPOC?",
        "Can I reschedule my interview?",
        "Is there a dress code?",
        "Can I participate before clearing the written examination?"
    ],

    # ==========================================================
    # CREATIVE COMPETITION
    # ==========================================================

    "CREATIVE COMPETITION": [

        "What is the Ekta Creative Competition 2025?",
        "What are the competition categories?",
        "How do I submit my entry?",
        "Is there any prize?",
        "Who can participate?"
    ],

    # ==========================================================
    # MIGRANT WORKERS
    # ==========================================================

    "MIGRANT WORKERS": [

        "How do I register as a migrant worker?",
        "What support does Ekta Trust provide to migrant workers?",
        "What documents are required for migrant registration?"
    ],

    # ==========================================================
    # ATROCITY REPORTING
    # ==========================================================

    "ATROCITY REPORTING": [

        "How do I report an atrocity?",
        "What information is required to report an atrocity?",
        "Who can report an atrocity case?"
    ],

    # ==========================================================
    # WEBSITE
    # ==========================================================

    "WEBSITE": [

        "What are the Terms and Conditions?",
        "How do I log into the website?",
        "I forgot my password.",
        "Who developed this website?",
        "What is the registered address of Ekta Trust?"
    ],

    # ==========================================================
    # NEWS
    # ==========================================================

    "NEWS": [

        "What are the latest news updates?",
        "Has Ekta Trust built any libraries recently?",
        "Are there any recent press releases?"
    ],

    # ==========================================================
    # OUT OF SCOPE
    # ==========================================================

    "OUT OF SCOPE": [

        "Who is the Prime Minister of India?",
        "What is today's weather?",
        "What is the price of an iPhone?",
        "Who won the FIFA World Cup?",
        "Tell me about Virat Kohli."
    ]

}


question_number = 1

overall_start = time.time()

for section_name, questions in TEST_SECTIONS.items():

    print("\n")
    print("=" * 100)
    print(f"SECTION : {section_name}")
    print("=" * 100)

    # New conversation for every topic
    session_id = create_session()

    for question in questions:

        print("\n")
        print("-" * 100)
        print(f"QUESTION {question_number}")
        print("-" * 100)
        print(question)

        start = time.time()

        try:

            result = generate_answer(
                session_id=session_id,
                question=question
            )

            total_time = time.time() - start

            print("\nANSWER:")
            print(result["answer"])

            print("\nSOURCES:")
            print(", ".join(result["sources"]))

            print(f"\nTIME: {total_time:.2f} sec")

        except Exception as error:

            print("\nERROR:")
            print(error)

        question_number += 1

print("\n")
print("=" * 100)
print("ALL TESTS COMPLETED")
print("=" * 100)

print(
    f"\nTOTAL TEST TIME : {time.time() - overall_start:.2f} seconds"
)