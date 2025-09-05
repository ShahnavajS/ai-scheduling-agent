# AI Scheduling Agent

This is my internship assignment project.  
It is a console-based Python program with SQLite database that:

- Identifies new vs. returning patients
- Assigns appointment duration (60/30 mins)
- Lets patients choose doctors and available slots
- Books and saves appointments
- Supports adding bulk patients
- Includes intake form distribution

## How to Run

```bash
# Reset and seed database
python main.py --reset

# Run the console app
python main.py
