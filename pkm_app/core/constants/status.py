from core.constants.strings import AppStrings
from models import ResourceStatus


STATUS_LABELS: dict[ResourceStatus, str] = {
    ResourceStatus.INBOX: AppStrings.FORM_STATUS_INBOX,
    ResourceStatus.PLANNED: AppStrings.FORM_STATUS_PLANNED,
    ResourceStatus.IN_PROGRESS: AppStrings.FORM_STATUS_IN_PROGRESS,
    ResourceStatus.COMPLETED: AppStrings.FORM_STATUS_COMPLETED,
}


def status_label(status: ResourceStatus) -> str:
    return STATUS_LABELS.get(status, status.value)


PRIORITY_LABELS: dict[int, str] = {
    1: "Yüksek",
    2: "Orta",
    3: "Düşük",
}


def priority_label(priority: int) -> str:
    return PRIORITY_LABELS.get(priority, str(priority))
