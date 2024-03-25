generate_emails.sh
#!/bin/bash
# Define arrays of first names, last names, and domains
firstNames=("james" "elizabeth" "michael" "emma" "david" "olivia" "william" "ava" "sophia" "lucas" "mia" "benjamin" "isabella" "ethan" "charlotte" "daniel" "abigail" "samuel" "grace" "jack")
lastNames=("pearson" "stone" "rivera" "watson" "white" "johnson" "brown" "miller" "davis" "lee" "hall" "clark" "lewis" "young" "green" "hernandez" "lopez" "martinez" "thomas" "moore")
domains=("digitalinbox" "quickpost" "mailworld" "e-message" "themailhub" "securemailspace" "letterbox" "postvault" "fastmailservice" "inboxdirect")
domainTypes=(".net" ".org" ".info" ".co" ".com")
# Function to generate a random email
generate_email() {
    local firstName=${firstNames[$RANDOM % ${#firstNames[@]}]}
    local lastName=${lastNames[$RANDOM % ${#lastNames[@]}]}
    local domain=${domains[$RANDOM % ${#domains[@]}]}
    local domainType=${domainTypes[$RANDOM % ${#domainTypes[@]}]}
    echo "$firstName.$lastName@$domain$domainType"
}
# Generate 50 email addresses
for i in {1..50}; do
    generate_email
done