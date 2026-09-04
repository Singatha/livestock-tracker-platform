from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.animals.models import Animal, AnimalLifecycleEvent, Flock
from apps.farms.models import Farm, FarmMembership
from apps.growth.models import WeightMeasurement
from apps.health.models import HealthObservation, Treatment
from apps.husbandry.models import HusbandryTask
from apps.medicine.models import (
    DoseAdministration,
    MedicineBatch,
    MedicineProduct,
    TreatmentCourse,
)
from apps.notifications.models import Notification
from apps.nutrition.models import Feed, FeedingPlan, FeedingPlanItem
from apps.reproduction.models import BirthRecord, BreedingRecord


class Command(BaseCommand):
    help = "Create a repeatable, dashboard-ready demonstration farm"

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", default="demo-password")

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        now = timezone.now()
        username = options["username"]
        password = options["password"]

        owner, _ = User.objects.update_or_create(
            username=username,
            defaults={
                "email": f"{username}@flockwise.local",
                "first_name": "Thandi",
                "last_name": "Mokoena",
                "is_active": True,
            },
        )
        owner.set_password(password)
        owner.save(update_fields=["password"])

        worker, _ = User.objects.update_or_create(
            username=f"{username}-worker",
            defaults={
                "email": f"{username}-worker@flockwise.local",
                "first_name": "Sipho",
                "last_name": "Dlamini",
                "is_active": True,
            },
        )
        worker.set_password(password)
        worker.save(update_fields=["password"])

        farm, _ = Farm.objects.update_or_create(
            owner=owner,
            name="Sunrise Smallholding",
        )
        FarmMembership.objects.update_or_create(
            farm=farm,
            user=owner,
            defaults={"role": FarmMembership.Role.OWNER, "is_active": True},
        )
        FarmMembership.objects.update_or_create(
            farm=farm,
            user=worker,
            defaults={"role": FarmMembership.Role.WORKER, "is_active": True},
        )

        flocks = self._seed_flocks(farm)
        animals = self._seed_animals(farm, flocks)
        self._seed_lifecycle_events(farm, owner, animals, today)
        self._seed_weights(farm, owner, animals, today)
        observations = self._seed_health(farm, owner, animals, now, today)
        self._seed_reproduction(farm, owner, animals, today)
        self._seed_medicine(farm, owner, animals, observations, now, today)
        self._seed_nutrition(farm, flocks, today)
        self._seed_tasks_and_notifications(farm, owner, worker, animals, flocks, now, today)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(f"Farm: {farm.name}")
        self.stdout.write(f"Login: {username} / {password}")
        self.stdout.write(f"Animals: {farm.animals.count()}")

    def _seed_flocks(self, farm):
        definitions = {
            "Breeding Ewes": "Mature breeding sheep and replacement ewes.",
            "Growing Stock": "Weaned lambs and kids monitored for growth.",
            "Goat Herd": "Breeding and production goats.",
        }
        return {
            name: Flock.objects.update_or_create(
                farm=farm,
                name=name,
                defaults={"description": description},
            )[0]
            for name, description in definitions.items()
        }

    def _seed_animals(self, farm, flocks):
        definitions = [
            (
                "SH-001",
                "Amara",
                "sheep",
                "Dorper",
                "female",
                date(2022, 8, 14),
                "Breeding Ewes",
                False,
                "active",
            ),
            (
                "SH-002",
                "Nandi",
                "sheep",
                "Dorper",
                "female",
                date(2023, 2, 3),
                "Breeding Ewes",
                True,
                "active",
            ),
            (
                "SH-003",
                "Atlas",
                "sheep",
                "Dorper",
                "male",
                date(2022, 5, 19),
                "Breeding Ewes",
                False,
                "active",
            ),
            (
                "SH-004",
                "Lindi",
                "sheep",
                "Merino",
                "female",
                date(2021, 11, 7),
                "Breeding Ewes",
                False,
                "active",
            ),
            (
                "SH-005",
                "Patches",
                "sheep",
                "Dorper",
                "female",
                date(2025, 9, 22),
                "Growing Stock",
                False,
                "active",
            ),
            ("SH-090", "", "sheep", "Merino", "male", date(2023, 4, 11), None, False, "sold"),
            (
                "GT-001",
                "Zola",
                "goat",
                "Boer",
                "female",
                date(2022, 10, 1),
                "Goat Herd",
                False,
                "active",
            ),
            (
                "GT-002",
                "Kaya",
                "goat",
                "Boer",
                "female",
                date(2023, 6, 18),
                "Goat Herd",
                True,
                "active",
            ),
            (
                "GT-003",
                "Rafiki",
                "goat",
                "Kalahari Red",
                "male",
                date(2022, 3, 27),
                "Goat Herd",
                False,
                "active",
            ),
            (
                "GT-004",
                "Bean",
                "goat",
                "Boer",
                "male",
                date(2025, 11, 2),
                "Growing Stock",
                False,
                "active",
            ),
            ("GT-090", "", "goat", "Boer", "female", date(2020, 1, 16), None, False, "deceased"),
        ]
        animals = {}
        for ear_tag, name, species, breed, sex, born, flock_name, attention, status in definitions:
            animal, _ = Animal.objects.update_or_create(
                farm=farm,
                ear_tag=ear_tag,
                defaults={
                    "name": name,
                    "species": species,
                    "breed": breed,
                    "sex": sex,
                    "date_of_birth": born,
                    "flock": flocks.get(flock_name),
                    "status": status,
                    "needs_attention": attention,
                    "notes": "Demonstration animal.",
                },
            )
            animals[ear_tag] = animal
        return animals

    def _seed_lifecycle_events(self, farm, owner, animals, today):
        for animal in animals.values():
            AnimalLifecycleEvent.objects.update_or_create(
                animal=animal,
                event_type=AnimalLifecycleEvent.EventType.REGISTERED,
                defaults={
                    "farm": farm,
                    "effective_date": min(animal.date_of_birth + timedelta(days=30), today),
                    "to_status": Animal.Status.ACTIVE,
                    "to_flock": animal.flock,
                    "reason": "Imported from the farm register",
                    "recorded_by": owner,
                },
            )

    def _seed_weights(self, farm, owner, animals, today):
        series = {
            "SH-001": ((60, "61.8"), (30, "63.0"), (2, "64.4")),
            "SH-002": ((60, "59.6"), (30, "58.9"), (2, "57.5")),
            "SH-005": ((60, "28.1"), (30, "32.4"), (2, "36.8")),
            "GT-001": ((60, "48.2"), (30, "49.1"), (2, "50.0")),
            "GT-002": ((60, "46.5"), (30, "47.2"), (2, "46.7")),
            "GT-004": ((60, "20.0"), (30, "23.2"), (2, "27.1")),
        }
        for ear_tag, measurements in series.items():
            for index, (days_ago, weight) in enumerate(measurements, start=1):
                WeightMeasurement.objects.update_or_create(
                    animal=animals[ear_tag],
                    notes=f"Demo growth measurement {index}",
                    defaults={
                        "farm": farm,
                        "measured_on": today - timedelta(days=days_ago),
                        "weight_kg": Decimal(weight),
                        "body_condition_score": Decimal("3.0"),
                        "recorded_by": owner,
                    },
                )

    def _seed_health(self, farm, owner, animals, now, today):
        definitions = [
            (
                "SH-002",
                "Possible internal parasite burden",
                "parasite",
                "high",
                2,
                False,
                "Pale eyelids and reduced appetite.",
            ),
            (
                "GT-002",
                "Limping on front left hoof",
                "injury",
                "medium",
                1,
                False,
                "Cleaned hoof; monitor for swelling.",
            ),
            (
                "SH-001",
                "Routine condition check",
                "general",
                "low",
                21,
                True,
                "Bright, alert, and in good condition.",
            ),
        ]
        observations = {}
        for ear_tag, summary, category, severity, days_ago, resolved, notes in definitions:
            observation, _ = HealthObservation.objects.update_or_create(
                farm=farm,
                animal=animals[ear_tag],
                summary=summary,
                defaults={
                    "observed_at": now - timedelta(days=days_ago),
                    "category": category,
                    "severity": severity,
                    "notes": notes,
                    "is_resolved": resolved,
                    "recorded_by": owner,
                },
            )
            observations[ear_tag] = observation

        Treatment.objects.update_or_create(
            farm=farm,
            animal=animals["GT-002"],
            reason="Hoof tenderness",
            defaults={
                "observation": observations["GT-002"],
                "administered_at": now - timedelta(days=1),
                "product": "Antiseptic hoof spray",
                "dosage": "Two sprays",
                "route": Treatment.Route.TOPICAL,
                "follow_up_date": today + timedelta(days=2),
                "notes": "Keep the animal on dry ground.",
                "administered_by": owner,
            },
        )
        return observations

    def _seed_reproduction(self, farm, owner, animals, today):
        confirmed, _ = BreedingRecord.objects.update_or_create(
            farm=farm,
            dam=animals["SH-001"],
            notes="Demo confirmed pregnancy",
            defaults={
                "sire": animals["SH-003"],
                "breeding_date": today - timedelta(days=129),
                "expected_birth_date": today + timedelta(days=18),
                "method": BreedingRecord.Method.NATURAL,
                "status": BreedingRecord.Status.CONFIRMED,
                "pregnancy_checked_on": today - timedelta(days=70),
                "recorded_by": owner,
            },
        )
        BreedingRecord.objects.update_or_create(
            farm=farm,
            dam=animals["GT-001"],
            notes="Demo overdue expected birth",
            defaults={
                "sire": animals["GT-003"],
                "breeding_date": today - timedelta(days=155),
                "expected_birth_date": today - timedelta(days=5),
                "method": BreedingRecord.Method.NATURAL,
                "status": BreedingRecord.Status.CONFIRMED,
                "pregnancy_checked_on": today - timedelta(days=95),
                "recorded_by": owner,
            },
        )
        completed, _ = BreedingRecord.objects.update_or_create(
            farm=farm,
            dam=animals["SH-004"],
            notes="Demo completed breeding",
            defaults={
                "sire": animals["SH-003"],
                "breeding_date": today - timedelta(days=180),
                "expected_birth_date": today - timedelta(days=33),
                "method": BreedingRecord.Method.NATURAL,
                "status": BreedingRecord.Status.COMPLETED,
                "pregnancy_checked_on": today - timedelta(days=120),
                "recorded_by": owner,
            },
        )
        BirthRecord.objects.update_or_create(
            breeding=completed,
            defaults={
                "farm": farm,
                "dam": animals["SH-004"],
                "birth_date": today - timedelta(days=32),
                "total_born": 2,
                "born_alive": 2,
                "stillborn": 0,
                "notes": "Healthy twin lambs.",
                "recorded_by": owner,
            },
        )
        return confirmed

    def _seed_medicine(self, farm, owner, animals, observations, now, today):
        dewormer, _ = MedicineProduct.objects.update_or_create(
            farm=farm,
            name="Ivermectin 1%",
            defaults={
                "active_ingredient": "Ivermectin",
                "concentration": "10 mg/ml",
                "stock_unit": "ml",
                "reorder_level": Decimal("30.00"),
                "meat_withdrawal_days": 28,
                "milk_withdrawal_days": 7,
                "instructions": "Dose according to live weight and veterinary guidance.",
            },
        )
        vaccine, _ = MedicineProduct.objects.update_or_create(
            farm=farm,
            name="Clostridial 8-in-1 Vaccine",
            defaults={
                "active_ingredient": "Clostridial antigens",
                "concentration": "2 ml/dose",
                "stock_unit": "ml",
                "reorder_level": Decimal("20.00"),
                "meat_withdrawal_days": 0,
                "milk_withdrawal_days": 0,
                "instructions": "Keep refrigerated and follow the label schedule.",
            },
        )
        dewormer_batch, _ = MedicineBatch.objects.update_or_create(
            product=dewormer,
            batch_number="DEMO-IVM-01",
            defaults={
                "farm": farm,
                "expiry_date": today + timedelta(days=24),
                "quantity_on_hand": Decimal("18.00"),
            },
        )
        MedicineBatch.objects.update_or_create(
            product=vaccine,
            batch_number="DEMO-VAC-01",
            defaults={
                "farm": farm,
                "expiry_date": today + timedelta(days=180),
                "quantity_on_hand": Decimal("60.00"),
            },
        )
        course, _ = TreatmentCourse.objects.update_or_create(
            farm=farm,
            animal=animals["SH-002"],
            product=dewormer,
            reason="Possible internal parasite burden",
            defaults={
                "dosage": "3 ml",
                "route": "Oral",
                "started_on": today - timedelta(days=1),
                "planned_doses": 2,
                "frequency_hours": 48,
                "status": TreatmentCourse.Status.ACTIVE,
                "meat_withdrawal_end_date": today + timedelta(days=27),
                "milk_withdrawal_end_date": today + timedelta(days=6),
                "notes": "Recheck eyelid colour after the second dose.",
                "prescribed_by": owner,
            },
        )
        DoseAdministration.objects.update_or_create(
            course=course,
            batch=dewormer_batch,
            notes="Demo first dose",
            defaults={
                "farm": farm,
                "administered_at": now - timedelta(days=1),
                "quantity_used": Decimal("3.00"),
                "administered_by": owner,
            },
        )
        Treatment.objects.update_or_create(
            farm=farm,
            animal=animals["SH-002"],
            reason="Possible internal parasite burden",
            defaults={
                "observation": observations["SH-002"],
                "administered_at": now - timedelta(days=1),
                "product": dewormer.name,
                "dosage": "3 ml",
                "route": Treatment.Route.ORAL,
                "withdrawal_end_date": today + timedelta(days=27),
                "follow_up_date": today + timedelta(days=2),
                "administered_by": owner,
            },
        )

    def _seed_nutrition(self, farm, flocks, today):
        hay, _ = Feed.objects.update_or_create(
            farm=farm,
            name="Lucerne Hay",
            defaults={
                "category": Feed.Category.FORAGE,
                "suitability": Feed.Suitability.BOTH,
                "unit": "kg",
                "quantity_on_hand": Decimal("420.00"),
                "reorder_level": Decimal("120.00"),
                "unit_cost": Decimal("5.80"),
                "notes": "Second-cut lucerne stored in the north shed.",
            },
        )
        pellets, _ = Feed.objects.update_or_create(
            farm=farm,
            name="Grower Pellets",
            defaults={
                "category": Feed.Category.CONCENTRATE,
                "suitability": Feed.Suitability.BOTH,
                "unit": "kg",
                "quantity_on_hand": Decimal("38.00"),
                "reorder_level": Decimal("50.00"),
                "unit_cost": Decimal("8.25"),
                "notes": "Low stock demonstration item.",
            },
        )
        mineral, _ = Feed.objects.update_or_create(
            farm=farm,
            name="Small-stock Mineral Mix",
            defaults={
                "category": Feed.Category.MINERAL,
                "suitability": Feed.Suitability.BOTH,
                "unit": "kg",
                "quantity_on_hand": Decimal("25.00"),
                "reorder_level": Decimal("10.00"),
                "unit_cost": Decimal("12.40"),
                "notes": "Offer free-choice under cover.",
            },
        )
        plan, _ = FeedingPlan.objects.update_or_create(
            farm=farm,
            flock=flocks["Growing Stock"],
            name="Growing stock daily ration",
            defaults={
                "life_stage": FeedingPlan.LifeStage.GROWING,
                "start_date": today - timedelta(days=30),
                "is_active": True,
                "notes": "Review quantities after each monthly weighing.",
            },
        )
        for feed, quantity, feeding_time in (
            (hay, "0.800", "Morning and late afternoon"),
            (pellets, "0.350", "Morning"),
            (mineral, "0.030", "Free choice"),
        ):
            FeedingPlanItem.objects.update_or_create(
                plan=plan,
                feed=feed,
                defaults={
                    "quantity_per_animal": Decimal(quantity),
                    "feeding_time": feeding_time,
                },
            )

    def _seed_tasks_and_notifications(self, farm, owner, worker, animals, flocks, now, today):
        definitions = [
            (
                "Follow up Nandi parasite treatment",
                "health_check",
                -1,
                animals["SH-002"],
                None,
                "Check appetite and FAMACHA score.",
            ),
            (
                "Inspect Kaya's hoof",
                "hoof_care",
                2,
                animals["GT-002"],
                None,
                "Confirm that the limp and swelling are improving.",
            ),
            (
                "Weigh growing stock",
                "weighing",
                6,
                None,
                flocks["Growing Stock"],
                "Record weights before the morning feed.",
            ),
            (
                "Annual clostridial vaccination",
                "vaccination",
                14,
                None,
                flocks["Breeding Ewes"],
                "Check vaccine stock and cold-chain records.",
            ),
        ]
        tasks = []
        for title, task_type, offset, animal, flock, notes in definitions:
            task, _ = HusbandryTask.objects.update_or_create(
                farm=farm,
                title=title,
                defaults={
                    "animal": animal,
                    "flock": flock,
                    "task_type": task_type,
                    "due_date": today + timedelta(days=offset),
                    "status": HusbandryTask.Status.SCHEDULED,
                    "reminder_days_before": 3,
                    "notes": notes,
                },
            )
            tasks.append(task)

        HusbandryTask.objects.update_or_create(
            farm=farm,
            title="Monthly breeding flock condition check",
            defaults={
                "flock": flocks["Breeding Ewes"],
                "task_type": HusbandryTask.TaskType.HEALTH_CHECK,
                "due_date": today - timedelta(days=7),
                "status": HusbandryTask.Status.COMPLETED,
                "recurrence_days": 30,
                "reminder_days_before": 2,
                "notes": "Score and record a representative group.",
                "completed_at": now - timedelta(days=7),
                "completion_notes": "Condition was generally good; Nandi flagged for review.",
                "completed_by": worker,
            },
        )

        for recipient in (owner, worker):
            overdue_task = tasks[0]
            Notification.objects.update_or_create(
                recipient=recipient,
                task=overdue_task,
                kind=Notification.Kind.TASK_OVERDUE,
                defaults={
                    "farm": farm,
                    "title": f"Overdue: {overdue_task.title}",
                    "message": f"SH-002 · due {overdue_task.due_date:%d %b %Y}",
                    "link": f"/animals/{animals['SH-002'].id}",
                },
            )
            upcoming_task = tasks[1]
            Notification.objects.update_or_create(
                recipient=recipient,
                task=upcoming_task,
                kind=Notification.Kind.TASK_DUE,
                defaults={
                    "farm": farm,
                    "title": f"Upcoming: {upcoming_task.title}",
                    "message": f"GT-002 · due {upcoming_task.due_date:%d %b %Y}",
                    "link": f"/animals/{animals['GT-002'].id}",
                },
            )
