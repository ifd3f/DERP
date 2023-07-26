from django.test import TestCase

from erp.models import CostCenter


class CostCenterPaths(TestCase):
    def test_paths_are_generated_correctly_on_create(self):
        cc1 = CostCenter.objects.create(
            name="Slush Fund",
            description="Gay",
        )
        cc2 = CostCenter.objects.create(
            name="Engineering",
            description="Gay",
            parent=cc1,
        )
        cc3 = CostCenter.objects.create(
            name="Chemistry",
            description="Gay",
            parent=cc2,
        )

        self.assertEqual(
            CostCenter.objects.get(id=cc3.id).path, f"/{cc1.id}/{cc2.id}/{cc3.id}"
        )

    def test_paths_are_generated_correctly_on_reparent(self):
        cc1 = CostCenter.objects.create(
            name="Slush Fund",
            description="Gay",
        )
        cc2 = CostCenter.objects.create(
            name="Engineering",
            description="Gay",
            parent=cc1,
        )
        cc3 = CostCenter.objects.create(
            name="Chemistry",
            description="Gay",
            parent=cc2,
        )
        cc4 = CostCenter.objects.create(
            name="Finance",
            description="Gay",
        )

        cc3.parent = cc4
        cc3.save()

        self.assertEqual(CostCenter.objects.get(id=cc3.id).path, f"/{cc4.id}/{cc3.id}")

    def test_transitive_paths_are_generated_correctly_on_reparent(self):
        cc1 = CostCenter.objects.create(
            name="Slush Fund",
            description="Gay",
        )
        cc2 = CostCenter.objects.create(
            name="Engineering",
            description="Gay",
            parent=cc1,
        )
        cc3 = CostCenter.objects.create(
            name="Chemistry",
            description="Gay",
            parent=cc2,
        )
        cc4 = CostCenter.objects.create(
            name="Finance",
            description="Gay",
        )
        cc5 = CostCenter.objects.create(name="Legal", description="Gay", parent=cc4)

        cc2.parent = cc5
        cc2.save()

        self.assertEqual(
            CostCenter.objects.get(id=cc2.id).path, f"/{cc4.id}/{cc5.id}/{cc2.id}"
        )
        self.assertEqual(
            CostCenter.objects.get(id=cc3.id).path,
            f"/{cc4.id}/{cc5.id}/{cc2.id}/{cc3.id}",
        )
