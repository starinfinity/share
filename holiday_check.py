from datetime import datetime, timedelta


def find_next_working_day(verify=False):
    # Define the list of holidays (example dates)
    holidays = ['2024-01-16', '2024-01-14', '2024-07-04']

    # Helper function to check if a date is a holiday
    def is_holiday(date):
        return date.strftime('%Y-%m-%d') in holidays

    # Helper function to find the next weekday given a start date and weekday number
    def find_next_weekday(start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    # Calculate next Tuesday
    today = datetime.now()
    next_tuesday = find_next_weekday(today, 1)  # 1 is for Tuesday

    if verify:
        # Verify if the condition for Tuesday is met
        if today.weekday() == 1 and not is_holiday(today):  # If today is Tuesday and not a holiday
            return True
        elif is_holiday(next_tuesday):
            # Find the day before Tuesday that is not a holiday
            prev_day = next_tuesday - timedelta(days=1)
            while prev_day.weekday() in [5, 6] or is_holiday(prev_day):  # Skip weekends and holidays
                prev_day -= timedelta(days=1)
            return today.date() == prev_day.date()
        else:
            return False
    else:
        # Find the next working day based on the conditions
        if not is_holiday(next_tuesday):
            return "0 17 * * 2"
        else:
            # Check Monday before Tuesday
            monday = next_tuesday - timedelta(days=1)
            # Check Friday before Monday
            friday = monday - timedelta(days=3)
            if not is_holiday(monday) and today.weekday() in [0, 6]:  # Sunday or Monday
                return "0 17 * * *"
            elif not is_holiday(friday) and today.weekday() in [3, 4]:  # Thursday or Friday
                return "0 17 * * *"
            else:
                return None


# Example usage
print(find_next_working_day())  # With default verify=False
print(find_next_working_day(verify=True))  # With verify=True
