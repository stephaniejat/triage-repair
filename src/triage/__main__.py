"""
Filename: src/triage/__main__.py
CLI execution

"""

from .model import PatientCase, patient_record

def main() -> None:
    case = PatientCase("demo", 0.53, 0.25)
    print(patient_record(case))

if __name__ == "__main__":
    main()
