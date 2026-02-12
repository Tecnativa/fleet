# Copyright 2021 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestFleetVehicleInspectionTemplate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection = cls.env["fleet.vehicle.inspection"]
        cls.inspection_item = cls.env["fleet.vehicle.inspection.item"]
        cls.inspection_template = cls.env["fleet.vehicle.inspection.template"]
        cls.vehicle = cls.env.ref("fleet.vehicle_5")
        cls.item_01 = cls.inspection_item.create({"name": "Lights"})
        cls.item_02 = cls.inspection_item.create({"name": "Mirrors"})
        cls.inspection_template_01 = cls.inspection_template.create(
            {
                "name": "TemplateTest_01",
                "inspection_template_line_ids": [
                    Command.create(
                        {"inspection_template_item_id": cls.item_01.id},
                    ),
                    Command.create(
                        {"inspection_template_item_id": cls.item_02.id},
                    ),
                ],
            }
        )
        cls.inspection_template_02 = cls.inspection_template.create(
            {
                "name": "TemplateTest_02",
                "inspection_template_line_ids": [
                    Command.create(
                        {
                            "inspection_template_item_id": cls.item_01.id,
                            "sequence": 11,  # Different sequence in the template line
                        },
                    ),
                    Command.create(
                        {
                            "inspection_template_item_id": cls.item_02.id,
                            "sequence": 10,  # Different sequence in the template line
                        },
                    ),
                ],
            }
        )

    def test_fleet_vehicle_inspection(self):
        # --- Test with an inspection template ---
        inspection_form = Form(self.env["fleet.vehicle.inspection"])
        inspection_form.vehicle_id = self.vehicle
        inspection_form.odometer = 10
        inspection_form.inspection_template_id = self.inspection_template_01
        self.assertEqual(inspection_form.name, self.inspection_template_01.name)
        self.assertTrue(inspection_form.inspection_line_ids)
        # --- Change the template ID ---
        inspection_form.inspection_template_id = self.inspection_template_02
        self.assertEqual(len(inspection_form.inspection_line_ids), 2)
        inspection = inspection_form.save()
        # Check if the sequence is correctly copied from the template line
        line_1 = inspection.inspection_line_ids.filtered(
            lambda linei: linei.inspection_item_id == self.item_01
        )
        self.assertEqual(line_1.sequence, 11)
        inspection_form = Form(inspection)
        # --- Test without an inspection template ---
        inspection_form.inspection_template_id = self.env[
            "fleet.vehicle.inspection.template"
        ]  # Remove the template
        # Assert that the name and note are not changed
        self.assertEqual(inspection_form.name, self.inspection_template_02.name)
        # (remains the same as the previous template)
        self.assertNotEqual(inspection_form.name, self.inspection_template_01.name)
        # Assert that the inspection lines are NOT removed
        self.assertTrue(inspection_form.inspection_line_ids)
        self.assertEqual(len(inspection_form.inspection_line_ids), 2)
