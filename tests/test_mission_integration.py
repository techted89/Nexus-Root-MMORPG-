
import pytest
from src.services.mission_service import MissionService
from src.services.job_service import JobService
from src.models.player import Player
from src.core.events import EventBus
from src.models.mission import Mission, MissionStatus, MissionType, MissionReward, MissionObjective

class MockRepository:
    def __init__(self):
        self.missions = {}

    def save(self, mission):
        self.missions[mission.id] = mission
        return mission

    def find_by_id(self, mission_id):
        return self.missions.get(mission_id)

    def count(self):
        return len(self.missions)

    def find_all(self):
        return list(self.missions.values())

    def find_by_player_and_status(self, player_id, status):
        return [m for m in self.missions.values() if m.player_id == player_id and m.status == status]

@pytest.fixture
def event_bus():
    return EventBus()

@pytest.fixture
def mock_repo():
    return MockRepository()

@pytest.fixture
def mission_service(mock_repo, event_bus):
    return MissionService(mock_repo, event_bus=event_bus)

@pytest.fixture
def job_service(event_bus):
    return JobService(event_bus=event_bus)

@pytest.fixture
def player():
    return Player("test_user_integration")

def test_story_mission_completion_via_job(player, mission_service, job_service, mock_repo, event_bus):
    # 1. Setup the story mission manually since _initialize_default_missions creates them for us,
    # but we need to start it.

    story_mission = mock_repo.find_by_id("story_001")
    assert story_mission is not None

    # Mark prereqs as done
    player.completed_missions.append("tutorial_003")

    # Simulate unlocking requirements
    story_mission.status = MissionStatus.AVAILABLE
    player.stats.level = 10 # ensure level req

    # Start the mission
    success = story_mission.start(player)
    assert success is True

    # Verify it's active
    player.active_missions.append(story_mission.id)
    active_missions = mission_service.get_active_missions(player)
    assert len(active_missions) == 1
    assert active_missions[0].id == "story_001"

    # 2. Complete a job
    jobs = job_service.generate_jobs_for_player(player, count=1)
    job = jobs[0]

    # Before completion, objective should be incomplete
    assert story_mission.objectives[0].is_completed is False

    # Complete job
    if job.job_type.value == "it_support":
        job_service.complete_job(player, job.id, choice_index=0)
    else:
        job_service.complete_job(player, job.id, script_output=job.script_expected_output)

    # 3. Verify mission updated
    # We need to manually check the mission state in the repo because the event handler should have updated it
    updated_mission = mock_repo.find_by_id("story_001")

    # The objective "complete_job" should be complete
    objective = next(obj for obj in updated_mission.objectives if obj.id == "complete_job")
    assert objective.is_completed is True

    # Mission status check
    # Now we pass the player data in the event, so we expect the mission to be fully COMPLETED.
    assert updated_mission.status == MissionStatus.COMPLETED
