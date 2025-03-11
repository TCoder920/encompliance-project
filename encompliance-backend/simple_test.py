def get_fallback_response(prompt, operation_type):
    """
    Provide a fallback response when API keys are not available or for demo mode.
    """
    prompt_lower = prompt.lower()
    
    if "ratio" in prompt_lower and operation_type == "daycare":
        return "Per § 746.1601 and § 746.1609, the child-to-caregiver ratio for 2-year-olds is 11:1 when children are grouped by age. This means one caregiver may supervise up to 11 two-year-old children. If you have more than 11 two-year-olds, you'll need additional caregivers to maintain this ratio."
    elif "background check" in prompt_lower:
        return "According to the standards, all employees, volunteers, and household members (for home-based operations) must undergo a background check before having contact with children in care. This includes a criminal history check, central registry check, and fingerprinting. These checks must be renewed periodically as specified in the minimum standards."
    elif "training" in prompt_lower or "hours" in prompt_lower:
        if operation_type == "daycare":
            return "Per § 746.1309, caregivers must complete a minimum of 24 clock hours of training annually. This training must include specific topics such as child development, guidance and discipline, age-appropriate activities, and health and safety."
        else:
            return "According to § 748.930, caregivers in GROs must complete a minimum of 30 clock hours of training annually, including topics specific to the needs of children in care."
    else:
        return "I'd be happy to help with your question. Could you provide more details about the specific compliance area you're inquiring about? I can provide information on ratios, background checks, training requirements, physical facilities, health practices, and other regulatory areas."

def test_fallback():
    """Test the fallback response function."""
    prompt = "What are the requirements for background checks?"
    operation_type = "daycare"
    
    response = get_fallback_response(prompt, operation_type)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_fallback() 