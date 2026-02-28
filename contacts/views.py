from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
from .models import Contact


@api_view(["GET", "POST"])
@transaction.atomic
def identify(request):
    email = request.data.get("email")
    phone = request.data.get("phoneNumber")

    if not email and not phone:
        return Response({"error": "email or phoneNumber required"}, status=400)

    matched_contacts = Contact.objects.filter(
        Q(email=email) | Q(phoneNumber=phone)
    )

    if not matched_contacts.exists():
        new_contact = Contact.objects.create(
            email=email,
            phoneNumber=phone,
            linkPrecedence="primary",
        )

        return Response({
            "contact": {
                "primaryContatctId": new_contact.id,
                "emails": [email] if email else [],
                "phoneNumbers": [phone] if phone else [],
                "secondaryContactIds": [],
            }
        })

    
    all_related_ids = set()

    queue = list(matched_contacts)

    while queue:
        current = queue.pop()
        if current.id in all_related_ids:
            continue

        all_related_ids.add(current.id)

        if current.linkPrecedence == "secondary" and current.linkedId:
            queue.append(current.linkedId)

        children = Contact.objects.filter(linkedId=current.id)
        queue.extend(children)

    all_contacts = Contact.objects.filter(id__in=all_related_ids).order_by("createdAt")

    primary_contact = all_contacts.first()

    for contact in all_contacts:
        if contact.id != primary_contact.id and contact.linkPrecedence == "primary":
            contact.linkPrecedence = "secondary"
            contact.linkedId = primary_contact
            contact.save()

    all_contacts = Contact.objects.filter(
        Q(id=primary_contact.id) | Q(linkedId=primary_contact.id)
    ).order_by("createdAt")

    existing_emails = set(filter(None, all_contacts.values_list("email", flat=True)))
    existing_phones = set(filter(None, all_contacts.values_list("phoneNumber", flat=True)))

    if (email and email not in existing_emails) or \
       (phone and phone not in existing_phones):

        Contact.objects.create(
            email=email,
            phoneNumber=phone,
            linkedId=primary_contact,
            linkPrecedence="secondary",
        )

        all_contacts = Contact.objects.filter(
            Q(id=primary_contact.id) | Q(linkedId=primary_contact.id)
        ).order_by("createdAt")


    emails = []
    phones = []
    secondary_ids = []

    for contact in all_contacts:
        if contact.email and contact.email not in emails:
            emails.append(contact.email)

        if contact.phoneNumber and contact.phoneNumber not in phones:
            phones.append(contact.phoneNumber)

        if contact.linkPrecedence == "secondary":
            secondary_ids.append(contact.id)

    if primary_contact.email:
        emails.remove(primary_contact.email)
        emails.insert(0, primary_contact.email)

    if primary_contact.phoneNumber:
        phones.remove(primary_contact.phoneNumber)
        phones.insert(0, primary_contact.phoneNumber)

    return Response({
        "contact": {
            "primaryContatctId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids,
        }
    })