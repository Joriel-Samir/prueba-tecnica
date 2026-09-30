from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException, ValidationError

from .uploads import parse_tabular_upload


def process_bulk_upload(upload, serializer_class, context=None):
    try:
        rows = parse_tabular_upload(upload)
    except ValueError as error:
        raise ValidationError({"file": str(error)}) from error

    created = 0
    errors = []
    for row_number, row in rows:
        try:
            with transaction.atomic():
                serializer = serializer_class(
                    data=row, context=context or {}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except APIException as error:
            details = error.detail
            if not isinstance(details, dict):
                details = {"non_field_errors": [str(details)]}
            errors.append({"row": row_number, "details": details})
        except IntegrityError:
            errors.append(
                {
                    "row": row_number,
                    "details": {
                        "non_field_errors": [
                            "The row conflicts with an existing database record."
                        ]
                    },
                }
            )
        else:
            created += 1

    return {"created": created, "total": len(rows), "errors": errors}
