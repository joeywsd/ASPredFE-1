# management/commands/send_notification.py
from django.core.management.base import BaseCommand
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from sequence_analyzer.models import SequenceSubmission
from decimal import Decimal, ROUND_CEILING

class Command(BaseCommand):
    help = "Groups unsent submissions and emails a summary table to each user"

    def handle(self, *args, **options):
        # 1. Fetch only records that need an email using select_related for SQL Join
        submissions = SequenceSubmission.objects.filter(result_date__isnull=False, email_sent=False).select_related('user')
        
        if not submissions.exists():
            self.stdout.write("No pending submissions to email.")
            return

        # 2. Group by user
        user_map = {}
        for submission in submissions:  
            # 1. Convert the float result to a Decimal string safely
            dec_val = Decimal(str(submission.result))
            
            # 2. Force exactly 5 decimals, rounding everything UP (CEILING)
            #    '0.00001' tells Python you want 5 decimal places
            quantized_val = dec_val.quantize(Decimal('0.00001'), rounding=ROUND_CEILING)
            
            # 3. Save it as a temporary string attribute on the object
            submission.rounded_result = str(quantized_val)

            user_map.setdefault(submission.user, []).append(submission)


        # 3. Establish ONE single network connection for the entire batch
        connection = get_connection()
        connection.open()
        
        email_messages = []
        sent_submission_ids = []

        for user, user_submissions in user_map.items():
            if not user.email:
                continue

            # Render your HTML table template 
            html_content = render_to_string('sequence_analyzer/email/notification.html', {'submissions': user_submissions})

            # To see the html rendered, make a html file for now
            with open("test_email.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            # Formulate the email object pinned to the active connection
            msg = EmailMultiAlternatives(
                subject="Your Grouped Submission Results",
                body=f"Hi {user.username},\n\nYou have {len(user_submissions)} new sequence submission results ready to view. Please log in to your dashboard to review them.",
                from_email="noreply@yourdomain.com",
                to=[user.email],
                connection=connection # <--- Crucial for connection pooling
            )
            msg.attach_alternative(html_content, "text/html")
            
            email_messages.append(msg)
            
            # Keep track of records to update later
            for submission in user_submissions:
                sent_submission_ids.append(submission.id)

        # 4. Fire the emails all at once across the pool
        if email_messages:
            connection.send_messages(email_messages)
            
            # 5. Bulk update the database so they aren't emailed again next cron run
            SequenceSubmission.objects.filter(id__in=sent_submission_ids).update(email_sent=True)

        connection.close()
        self.stdout.write(f"Successfully sent summary emails to {len(user_map)} users.")
