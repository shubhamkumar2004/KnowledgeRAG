import time

from app.rag.generator import generate_answer


questions = [

    # Organization
    "What is Ekta Trust's vision?",
    "What is Ekta Trust's motto?",
    "What are the objectives of Ekta Trust?",
    "How can I volunteer or join the trust?",
    "How do I report an atrocity case?",
    "What tax benefits apply to donations (80G/12A)?",
    "How can I donate to Ekta Trust?",
    "What is the WhatsApp number for queries?",

    # Training
    "What training courses are offered?",
    "Is there a stipend for skill training programs?",

    # Run for Equality
    "Where does the run route go?",
    "What is the SOP for participants?",
    "Who won last year's Run for Equality?",
    "Can I see photos from the 2026 run?",
    "Is there a theme song for the event?",
    "Have any celebrities endorsed the event?",
    "Where is the Bib Expo?",

    # MIP
    "What documents are needed to register for MIP?",
    "How do I register as a faculty member?",
    "Is MIP free?",
    "Can I reschedule my interview?",

    # Creative Competition
    "What is Ekta Shapath?",
    "Can I read the Preamble in Hindi?",
    "What are the rules for Ekta Creative Competition 2025?",
    "How do I submit an entry?",
    "Is there a prize for winners?",

    # Website
    "How do I login?",
    "How do I reset my password?",
    "What are the Terms and Conditions?",
    "Who developed this website?",
    "What is the registered address?"
]


for index, question in enumerate(questions, start=1):

    print("\n" + "=" * 80)
    print(f"QUESTION {index}:")
    print(question)
    print("=" * 80)

    start = time.time()

    try:
        answer = generate_answer(question)

        total_time = time.time() - start

        print("\nANSWER:")
        print(answer)

        print(
            f"\nQUESTION TOTAL TIME: "
            f"{total_time:.2f} seconds"
        )

    except Exception as error:

        print("\nERROR:")
        print(error)