# A simple menu for exploring UdyamSathi.

def show_about():
    print("\nUdyamSathi helps small-business starters understand PMEGP and CMEGP.")


def show_sample_questions():
    print("\nSample questions:")
    print("- Am I eligible for PMEGP?")
    print("- How much subsidy could I receive?")
    print("- What documents are needed for CMEGP?")
    print()
    print("These are just the sample questions. For more features, stay TUNED !!!")


def check_sample_rule():
    age = int(input("\nPlease Enter your age: "))
    if age >= 18:
        print("Based on age alone, you meet this sample minimum-age check.")
    else:
        print("Based on age alone, you do not meet this sample minimum-age check.")
    print()
    print("This is only a demonstration rule, not a final government eligibility decision. for more features stay TUNED !!!")


while True:
    print("\n=== UdyamSathi Menu ===")
    print("1. About UdyamSathi")
    print("2. Sample questions")
    print("3. Sample eligibility rule check")
    print("0. Exit")

    choice = input("Choose an option: ").strip()

    if choice == "1":
        show_about()
    elif choice == "2":
        show_sample_questions()
    elif choice == "3":
        check_sample_rule()
    elif choice == "0":
        print("Goodbye! Have a NICE DAY")
        break
    else:
        print("Please choose a valid option.")
