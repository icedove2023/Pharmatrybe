from unittest.mock import MagicMock

from app.database.repositories.clinical_case_repository import ClinicalCaseRepository


class FakeEntity:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_clinical_case_repository_create_commits_and_refreshes():
    session = MagicMock()
    entity = FakeEntity(id=1)
    repository = ClinicalCaseRepository(session, entity_type=FakeEntity)

    repository.create(entity)

    session.add.assert_called_once_with(entity)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(entity)


def test_clinical_case_repository_get_by_id_returns_entity():
    session = MagicMock()
    entity = FakeEntity(id=1)
    session.get.return_value = entity
    repository = ClinicalCaseRepository(session, entity_type=FakeEntity)

    result = repository.get_by_id(1)

    session.get.assert_called_once_with(FakeEntity, 1)
    assert result is entity


def test_clinical_case_repository_list_returns_entities(monkeypatch):
    session = MagicMock()
    entity = FakeEntity(id=1)
    session.scalars.return_value.all.return_value = [entity]

    monkeypatch.setattr(
        "app.database.repositories.clinical_case_repository.select",
        lambda entity_type: "statement",
    )

    repository = ClinicalCaseRepository(session, entity_type=FakeEntity)
    results = repository.list(skip=0, limit=None)

    session.scalars.assert_called_once_with("statement")
    assert results == [entity]


def test_clinical_case_repository_get_all_invokes_list(monkeypatch):
    session = MagicMock()
    entity = FakeEntity(id=1)
    session.scalars.return_value.all.return_value = [entity]

    monkeypatch.setattr(
        "app.database.repositories.clinical_case_repository.select",
        lambda entity_type: "statement",
    )

    repository = ClinicalCaseRepository(session, entity_type=FakeEntity)
    results = repository.get_all()

    session.scalars.assert_called_once_with("statement")
    assert results == [entity]


def test_clinical_case_repository_update_modifies_and_refreshes():
    session = MagicMock()
    entity = FakeEntity(id=1, name="original")
    session.get.return_value = entity
    repository = ClinicalCaseRepository(session, entity_type=FakeEntity)

    result = repository.update(1, name="updated")

    assert result is entity
    assert entity.name == "updated"
    session.add.assert_called_once_with(entity)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(entity)


def test_clinical_case_repository_delete_removes_entity():
    session = MagicMock()
    entity = FakeEntity(id=1)
    session.get.return_value = entity
    repository = ClinicalCaseRepository(session, entity_type=FakeEntity)

    repository.delete(1)

    session.delete.assert_called_once_with(entity)
    session.commit.assert_called_once()
