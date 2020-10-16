__author__ = "Vini Salazar"
__license__ = "MIT"
__maintainer__ = "Vini Salazar"
__url__ = "https://github.com/vinisalazar/bioprov"
__version__ = "0.1.6"

"""
Module containing base provenance attributes.

This module extracts system-level information, such as user and environment
settings, and stores them. It is invoked to export provenance objects. 
"""
from bioprov import Project
from bioprov.utils import Warnings, build_prov_attributes
from prov.model import ProvDocument


# class BioProvDocument:
#     """
#     Class containing base provenance information for a Prov ProvDocument.
#
#     Adds two default namespaces: 'user', with present user and associated ProvAgent, and 'environment', with
#     present environment variables and associated ProvEntity
#     """
#
#     def __init__(self, _add_default_namespaces=True, _add_environ_attributes=True):
#         """
#         Constructor for the base provenance class.
#         Creates a prov.model.ProvDocument instance and loads the main attributes.
#         :param _add_default_namespaces: Whether to add namespaces when initiating.
#         """
#
#         # Initialize ProvDocument
#         self.ProvDocument = ProvDocument()
#         self.env = EnvProv()
#         self.user = self.env.user
#         self.user_agent = None
#         self.env_entity = None
#         self.project = None
#         self._add_environ_attributes = _add_environ_attributes
#
#         if _add_default_namespaces:
#             self._add_default_namespaces()
#
#     def _add_environ_namespace(self):
#         self.ProvDocument.add_namespace(self.env.env_namespace)
#         if self._add_environ_attributes:
#             self.env_entity = self.ProvDocument.entity(
#                 "env:{}".format(self.env),
#                 other_attributes=build_prov_attributes(
#                     self.env.env_dict, self.env.env_namespace
#                 ),
#             )
#         else:
#             self.env_entity = self.ProvDocument.entity("env:{}".format(self.env),)
#
#     def _add_user_namespace(self):
#         self.ProvDocument.add_namespace("user", self.user)
#         self.user_agent = self.ProvDocument.agent("user:{}".format(self.user))
#
#     def _add_default_namespaces(self):
#         self._add_environ_namespace()
#         self._add_user_namespace()
#
#     def _update_env(self):
#         """
#         Updates self.env attribute with current env.
#         :return: Updated self.env.
#         """
#         self.env = self.env.update()


class BioProvDocument:
    """
    Class containing base provenance information for a Project.
    """

    def __init__(
        self, project, _add_project_namespaces=True, add_attributes=True, **kwargs
    ):
        """
        Constructs base provenance for a Project.
        :param project: Project being processed.
        :param kwargs: Keyword arguments to be passed to BioProvDocument.__init__().
        """

        # Assert Project is good before constructing instance
        assert isinstance(project, Project), Warnings()["incorrect_type"](
            project, Project
        )
        self.ProvDocument = ProvDocument()
        self.project = project
        self.samples_entity = None
        self.activities = None
        self.add_attributes = add_attributes

        # Add default namespaces
        if _add_project_namespaces:
            self._add_project_namespaces()

        # Update relationships
        self._add_relationships()

    # def __repr__(self):
    #     return "BioProvDocument describing Project '{}' with {} samples.".format(
    #         self.project.tag, len(self.project)
    #     )

    def _add_project_namespaces(self):
        """
        Runs the three _add_namespace functions.
        :return:
        """
        self._add_project_namespace()
        self._add_samples_namespace()
        self._add_activities_namespace()
        self._add_env_and_user_namespace()
        self._iter_samples()

    def _add_env_and_user_namespace(self):
        self.ProvDocument.add_namespace(
            "envs", f"Environments associated with BioProv Project '{self.project.tag}'"
        )
        self.ProvDocument.add_namespace(
            "users", f"Users associated with BioProv Project '{self.project.tag}'"
        )

        for _user, _env in self.project.envs.items():
            if self.add_attributes:
                self.ProvDocument.entity(
                    f"envs:{_env}",
                    other_attributes=build_prov_attributes(
                        _env.env_dict, _env.env_namespace
                    ),
                )
            else:
                self.ProvDocument.entity(f"envs:{_env}")

            self.ProvDocument.agent(f"users:{_user}")

    #     def _add_environ_namespace(self):
    #         self.ProvDocument.add_namespace(self.env.env_namespace)
    #         if self._add_environ_attributes:
    #             self.env_entity = self.ProvDocument.entity(
    #                 "env:{}".format(self.env),
    #                 other_attributes=build_prov_attributes(
    #                     self.env.env_dict, self.env.env_namespace
    #                 ),
    #             )
    #         else:
    #             self.env_entity = self.ProvDocument.entity("env:{}".format(self.env),)

    def _add_project_namespace(self):
        self.project.namespace = self.ProvDocument.add_namespace(
            "project", str(self.project)
        )
        if self.add_attributes:
            self.project.entity = self.ProvDocument.entity(
                "project:{}".format(self.project),
                other_attributes=build_prov_attributes(
                    {
                        k: v
                        for k, v in self.project.__dict__.items()
                        if k not in ("_samples", "files")
                    },
                    self.project.namespace,
                ),
            )
        else:
            self.project.entity = self.ProvDocument.entity(
                "project:{}".format(self.project)
            )
        # # Check if project_csv exists
        # if "project_csv" in self.project.files.keys():
        #     self.project_file_entity = self.ProvDocument.entity(
        #         "project:{}".format(self.project.files["project_csv"])
        #     )
        # else:
        #     pass

    def _add_samples_namespace(self):

        self.ProvDocument.add_namespace(
            "samples",
            "Samples associated with bioprov Project '{}'".format(self.project.tag),
        )

    def _iter_envs(self):
        for _user, _env in self.project.envs.items():
            self.ProvDocument.bundle(f"users:{_user}")

    def _iter_samples(self):
        for _, sample in self.project.items():

            # Sample PROV attributes: bundle, namespace, entity
            sample.ProvBundle = self.ProvDocument.bundle(
                "samples:{}".format(sample.name)
            )
            sample.ProvBundle.set_default_namespace(sample.name)
            sample.ProvEntity = sample.ProvBundle.entity(sample.name)

            # Files PROV attributes: namespace, entities
            files_namespace_prefix = "{}.files".format(sample.name)
            sample.ProvBundle.add_namespace(
                files_namespace_prefix,
                "Files associated with Sample {}".format(sample.name),
            )
            for key, file in sample.files.items():
                file.namespace = sample.ProvBundle.add_namespace(
                    file.name, str(file.path)
                )
                file.ProvEntity = sample.ProvBundle.entity(
                    "{}:{}".format(files_namespace_prefix, file.name),
                    other_attributes=build_prov_attributes(
                        file.__dict__, file.namespace
                    ),
                )
                sample.ProvBundle.wasDerivedFrom(
                    file.ProvEntity, sample.ProvEntity,
                )

            # Programs PROV attributes: namespace, entities
            programs_namespace_prefix = "{}.programs".format(sample.name)
            for key, program in sample.programs.items():
                program.namespace = sample.ProvBundle.add_namespace(
                    program.name, str(program)
                )
                last_run = program.runs[str(len(program.runs))]
                program.ProvActivity = sample.ProvBundle.activity(
                    "{}:{}".format(programs_namespace_prefix, program.name),
                    startTime=last_run.start_time,
                    endTime=last_run.end_time,
                )
                # self.ProvDocument.wasAssociatedWith(
                #     program.ProvActivity, self.project.envs[last_run.user]
                # )

                # # Relationships based on Parameters
                # inputs = [parameter for parameter in program.params]

    def _add_activities_namespace(self):
        """
        Add activities Namespace to self
        :return:
        """

        if len(self.ProvDocument.namespaces) == 0:
            self.ProvDocument.add_namespace(
                "activities",
                "Activities associated with bioprov Project '{}'".format(
                    self.project.tag
                ),
            )

        # # Activities
        # self.activities = {
        #     "import_Project": self.ProvDocument.activity(
        #         "activities:{}".format("bioprov.Project")
        #     ),
        #     "import_Sample": self.ProvDocument.activity(
        #         "activities:{}".format("bioprov.Sample")
        #     ),
        # }

    def _add_relationships(self):
        pass
        # Relating project with user, project file, and sample
        # self.ProvDocument.wasAttributedTo(
        #     self.project.ProvEntity, "user:{}".format(self.user)
        # )
        # # Add activities
        # for key, activity in self.activities.items():
        #     self.ProvDocument.wasAssociatedWith(activity, "user:{}".format(self.user))
        # self.ProvDocument.wasGeneratedBy(
        #     self.project.ProvEntity, self.activities["import_Project"]
        # )
        # if self.project_file_entity is not None:
        #     self.ProvDocument.used(
        #         self.activities["import_Project"], self.project_file_entity
        #     )
        # self.ProvDocument.used(self.activities["import_Sample"], self.project.ProvEntity)
        # self.ProvDocument.wasGeneratedBy(
        #     self.samples_entity, self.activities["import_Sample"]
        # )
        # self.ProvDocument.wasAttributedTo(self.env_entity, self.user_agent)
