#!/bin/bash

DATAFILE="addressbook.txt"

touch "$DATAFILE"

# Function to display menu
menu() {
    echo "==============================="
    echo " Address Book Menu"
    echo "==============================="
    echo "1. Search Address Book"
    echo "2. Add Entry"
    echo "3. Remove Entry"
    echo "4. Display All Records"
    echo "5. Exit"
    echo "==============================="
}

# Function to search entries
search_entry() {
    echo -n "Enter search term (Name, Surname, Email, or Phone): "
    read term
    grep -i "$term" "$DATAFILE" || echo "No matching records found."
}

# Function to add entry
add_entry() {
    echo -n "Enter Name: "
    read name
    echo -n "Enter Surname: "
    read surname
    echo -n "Enter Email: "
    read email
    echo -n "Enter Phone: "
    read phone

    echo "Confirm adding record: $name|$surname|$email|$phone ? (y/n)"
    read confirm
    if [ "$confirm" = "y" ]; then
        echo "$name|$surname|$email|$phone" >> "$DATAFILE"
        echo "Record added successfully!"
    else
        echo "Cancelled."
    fi
}

# Function to remove entry
remove_entry() {
    echo -n "Enter search term to remove: "
    read term
    matches=$(grep -ni "$term" "$DATAFILE")

    if [ -z "$matches" ]; then
        echo "No matching records found."
        return
    fi

    echo "Matching records:"
    echo "$matches"
    echo -n "Enter line number of record to delete: "
    read lineno

    sed -i "${lineno}d" "$DATAFILE"
    echo "Record deleted successfully!"
}

# Function to display all entries
display_entries() {
    if [ ! -s "$DATAFILE" ]; then
        echo "No records in address book."
    else
        nl -w2 -s". " "$DATAFILE"
    fi
}

# Main program loop
while true
do
    menu
    echo -n "Choose an option [1-5]: "
    read choice
    case $choice in
        1) search_entry ;;
        2) add_entry ;;
        3) remove_entry ;;
        4) display_entries ;;
        5) echo "Exiting..."; break ;;
        *) echo "Invalid choice, try again." ;;
    esac
    echo
done

