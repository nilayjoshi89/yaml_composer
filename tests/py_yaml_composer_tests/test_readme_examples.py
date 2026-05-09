from typing import Any

import pytest

from py_yaml_composer.actions.default_actions import DefaultActions
from py_yaml_composer.generator.yaml_generator import YamlGenerator
from py_yaml_composer.traverser.basic_dfs import YamlTraverser
from tests.py_yaml_composer_tests.mock_file_helper import MockFileHelper


class _Base:
    """Shared setup/assertion helpers."""

    def create_generator(self, input_yaml_data: dict[str, Any]) -> None:
        input_data: dict[str, Any] = {
            "X-OUTPUT": MockFileHelper.output_file
        } | input_yaml_data
        self.mock_file_helper: MockFileHelper = MockFileHelper(
            {MockFileHelper.input_file: input_data}
        )
        self.generator: YamlGenerator = YamlGenerator(
            file_helper=self.mock_file_helper,
            traverser=YamlTraverser(),
            multistage_actions=DefaultActions.get(),
        )

    def create_generator_with_refs(
        self,
        input_yaml_data: dict[str, Any],
        ref_files: dict[str, dict[str, Any]],
    ) -> None:
        self.create_generator(input_yaml_data)
        for file_name, content in ref_files.items():
            self.mock_file_helper.setup_ref_file(file_name, content)

    def verify_no_diff(self, expected_output: dict[str, Any]) -> None:
        diff = self.mock_file_helper.diff_output(expected_output)
        assert diff == {}

    def run(self, expected_output: dict[str, Any]) -> None:
        self.generator.start(MockFileHelper.input_file)
        self.verify_no_diff(expected_output)


# ---------------------------------------------------------------------------
# README Simple Examples 1-5
# ---------------------------------------------------------------------------


class TestReadmeSimpleExamples(_Base):
    def test_example1_basic_reference_replacement(self) -> None:
        # README Example 1
        self.create_generator(
            {
                "X-OVERRIDE": {
                    "X-REF-Node2": {"name": "ServiceB", "value": "ValueB"}
                },
                "Node1": "ValueA",
                "X-REF-Node2": None,
            }
        )
        self.run({"Node1": "ValueA", "name": "ServiceB", "value": "ValueB"})

    def test_example2_nested_references(self) -> None:
        # README Example 2
        self.create_generator(
            {
                "X-OVERRIDE": {
                    "X-REF-DatabaseConfig": {
                        "connection_string": "postgresql://localhost:5432",
                        "pool_size": 20,
                    },
                    "X-REF-CacheConfig": {
                        "connection_string": "redis://localhost:6379",
                        "ttl": 3600,
                    },
                },
                "application": {
                    "database": {"X-REF-DatabaseConfig": None},
                    "cache": {"X-REF-CacheConfig": None},
                },
            }
        )
        self.run(
            {
                "application": {
                    "database": {
                        "connection_string": "postgresql://localhost:5432",
                        "pool_size": 20,
                    },
                    "cache": {
                        "connection_string": "redis://localhost:6379",
                        "ttl": 3600,
                    },
                }
            }
        )

    def test_example3_function_single_argument(self) -> None:
        # README Example 3
        self.create_generator(
            {
                "X-OVERRIDE": {
                    "X-REF-ServiceTemplate": {
                        "version": "{X-ARG-1}",
                        "enabled": True,
                    }
                },
                "services": {"api": {"X-REF-ServiceTemplate('v2.1')": None}},
            }
        )
        self.run({"services": {"api": {"version": "v2.1", "enabled": True}}})

    def test_example4_function_multiple_arguments(self) -> None:
        # README Example 4
        self.create_generator(
            {
                "X-OVERRIDE": {
                    "X-REF-ApiEndpoint": {
                        "path": "{X-ARG-1}",
                        "method": "{X-ARG-2}",
                        "auth_required": "{X-ARG-3}",
                    }
                },
                "endpoints": {
                    "users": {
                        "X-REF-ApiEndpoint('/api/users', 'GET', 'true')": None
                    }
                },
            }
        )
        self.run(
            {
                "endpoints": {
                    "users": {
                        "path": "/api/users",
                        "method": "GET",
                        "auth_required": "true",
                    }
                }
            }
        )

    def test_example5_list_substitution(self) -> None:
        # README Example 5 — list ref must be a dict VALUE, not a dict key
        self.create_generator(
            {
                "X-OVERRIDE": {"X-REF-PERMISSIONS": ["read", "write", "delete"]},
                "roles": {"admin": {"permissions": "X-REF-PERMISSIONS"}},
            }
        )
        self.run(
            {"roles": {"admin": {"permissions": ["read", "write", "delete"]}}}
        )


# ---------------------------------------------------------------------------
# README Advanced Examples 6-8
# ---------------------------------------------------------------------------


class TestReadmeAdvancedExamples(_Base):
    def test_example6_template_inheritance_via_include(self) -> None:
        # README Example 6 — base config inherited across two included files
        self.create_generator_with_refs(
            {
                "X-INCLUDE": ["templates/base.yml", "templates/components.yml"],
                "components": {"api": {"X-REF-API-COMPONENT": None}},
            },
            ref_files={
                "templates/base.yml": {
                    "X-REF-BASE-CONFIG": {
                        "timeout": 30,
                        "retry": 3,
                        "logging_level": "INFO",
                    }
                },
                "templates/components.yml": {
                    "X-REF-API-COMPONENT": {
                        "X-REF-BASE-CONFIG": None,
                        "endpoint": "/api/v1",
                        "rate_limit": 1000,
                    }
                },
            },
        )
        self.run(
            {
                "components": {
                    "api": {
                        "timeout": 30,
                        "retry": 3,
                        "logging_level": "INFO",
                        "endpoint": "/api/v1",
                        "rate_limit": 1000,
                    }
                }
            }
        )

    def test_example7_environment_specific_overrides_dev(self) -> None:
        # README Example 7 — dev environment
        self.create_generator_with_refs(
            {
                "X-INCLUDE": ["templates/database.yml"],
                "X-OVERRIDE": {
                    "X-REF-DB-NAME": "dev_db",
                    "X-REF-DB-HOST": "localhost",
                    "X-REF-DB-USER": "dev_user",
                    "X-REF-DB-PASSWORD": "dev_password",
                },
                "database": {
                    "X-REF-DATABASE-CONFIG(X-REF-DB-NAME, X-REF-DB-HOST, X-REF-DB-USER, X-REF-DB-PASSWORD)": None
                },
            },
            ref_files={
                "templates/database.yml": {
                    "X-REF-DATABASE-CONFIG": {
                        "name": "{X-ARG-1}",
                        "host": "{X-ARG-2}",
                        "credentials": {
                            "user": "{X-ARG-3}",
                            "password": "{X-ARG-4}",
                        },
                    }
                }
            },
        )
        self.run(
            {
                "database": {
                    "name": "dev_db",
                    "host": "localhost",
                    "credentials": {
                        "user": "dev_user",
                        "password": "dev_password",
                    },
                }
            }
        )

    def test_example7_environment_specific_overrides_prod(self) -> None:
        # README Example 7 — prod environment (same template, different overrides)
        self.create_generator_with_refs(
            {
                "X-INCLUDE": ["templates/database.yml"],
                "X-OVERRIDE": {
                    "X-REF-DB-NAME": "prod_db",
                    "X-REF-DB-HOST": "db.prod.internal",
                    "X-REF-DB-USER": "prod_user",
                    "X-REF-DB-PASSWORD": "${PROD_DB_PASSWORD:?error}",
                },
                "database": {
                    "X-REF-DATABASE-CONFIG(X-REF-DB-NAME, X-REF-DB-HOST, X-REF-DB-USER, X-REF-DB-PASSWORD)": None
                },
            },
            ref_files={
                "templates/database.yml": {
                    "X-REF-DATABASE-CONFIG": {
                        "name": "{X-ARG-1}",
                        "host": "{X-ARG-2}",
                        "credentials": {
                            "user": "{X-ARG-3}",
                            "password": "{X-ARG-4}",
                        },
                    }
                }
            },
        )
        self.run(
            {
                "database": {
                    "name": "prod_db",
                    "host": "db.prod.internal",
                    "credentials": {
                        "user": "prod_user",
                        "password": "${PROD_DB_PASSWORD:?error}",
                    },
                }
            }
        )

    def test_example8_composite_argument_interpolation(self) -> None:
        # README Example 8 — each field supports ONE {X-ARG-N} placeholder;
        # the placeholder can be embedded inside a larger string (prefix/suffix preserved)
        self.create_generator(
            {
                "X-OVERRIDE": {
                    "X-REF-ServiceDef": {
                        "service_id": "svc-{X-ARG-1}",
                        "registry": "mycompany/{X-ARG-2}",
                    }
                },
                "services": {
                    "processor": {"X-REF-ServiceDef('prod', 'data:v2.1')": None}
                },
            }
        )
        self.run(
            {
                "services": {
                    "processor": {
                        "service_id": "svc-prod",
                        "registry": "mycompany/data:v2.1",
                    }
                }
            }
        )


# ---------------------------------------------------------------------------
# README Real-World Example — Docker Compose (PostgreSQL + PgAdmin)
# This mirrors the actual repo/stack/pg_db_admin setup.
# ---------------------------------------------------------------------------

_BASE_TEMPLATE: dict[str, Any] = {
    "environment": ["TZ=Asia/Singapore"],
    "restart": "unless-stopped",
    "security_opt": ["no-new-privileges:true"],
    "pids_limit": 100,
    "mem_limit": "512m",
    "cpus": "1.0",
}

_POSTGRES_TEMPLATE: dict[str, Any] = {
    "X-REF-BASE-TEMPLATE": None,
    "image": "X-REF-IMAGE-POSTGRES",
    "container_name": "{X-ARG-1}",
    "shm_size": "128mb",
    "environment": ["{X-ARG-2}"],
    "ports": ["{X-ARG-3}"],
    "volumes": ["{X-ARG-4}"],
    "healthcheck": {
        "test": ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"],
        "interval": "10s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
    },
}

_PG_ADMIN_TEMPLATE: dict[str, Any] = {
    "X-REF-BASE-TEMPLATE": None,
    "image": "X-REF-IMAGE-PG-ADMIN4",
    "container_name": "{X-ARG-1}",
    "environment": "{X-ARG-2}",
    "ports": ["{X-ARG-3}"],
    "volumes": ["{X-ARG-4}"],
}

_CORE_FILE: dict[str, Any] = {"X-REF-BASE-TEMPLATE": _BASE_TEMPLATE}
_IMAGE_VERSION_FILE: dict[str, Any] = {
    "X-REF-IMAGE-POSTGRES": "postgres:18.3-alpine",
    "X-REF-IMAGE-PG-ADMIN4": "dpage/pgadmin4",
}
_POSTGRES_FILE: dict[str, Any] = {
    "X-REF-FUNCT-TEMPLATE-POSTGRES": _POSTGRES_TEMPLATE
}
_PG_ADMIN_FILE: dict[str, Any] = {
    "X-REF-FUNCT-TEMPLATE-PG-ADMIN": _PG_ADMIN_TEMPLATE
}


def _postgres_service(
    container: str,
    env_vars: list[str],
    ports: list[str],
    volumes: list[str],
    network: str,
) -> dict[str, Any]:
    return {
        "image": "postgres:18.3-alpine",
        "container_name": container,
        "restart": "unless-stopped",
        "environment": ["TZ=Asia/Singapore", *env_vars],
        "ports": ports,
        "volumes": volumes,
        "networks": [network],
        "healthcheck": {
            "test": [
                "CMD-SHELL",
                "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB",
            ],
            "interval": "10s",
            "timeout": "5s",
            "retries": 5,
            "start_period": "15s",
        },
        "shm_size": "128mb",
        "security_opt": ["no-new-privileges:true"],
        "pids_limit": 100,
        "mem_limit": "512m",
        "cpus": "1.0",
    }


class TestReadmeRealWorldDockerCompose(_Base):
    def _setup_stack(self, overrides: dict[str, Any]) -> None:
        self.create_generator_with_refs(
            {
                "X-INCLUDE": [
                    "templates/core.yml",
                    "templates/image_version.yml",
                    "templates/postgres.yml",
                    "templates/pg_admin.yml",
                ],
                "X-OVERRIDE": overrides,
                "services": {
                    "db-one": {
                        "X-REF-FUNCT-TEMPLATE-POSTGRES(X-REF-DB1-CONTAINER-NAME,X-REF-DB1-ENV,X-REF-DB1-PORTS,X-REF-DB1-VOLUME)": None,
                        "networks": ["pg_service_network"],
                    },
                    "db-two": {
                        "X-REF-FUNCT-TEMPLATE-POSTGRES(X-REF-DB2-CONTAINER-NAME,X-REF-DB2-ENV,X-REF-DB2-PORTS,X-REF-DB2-VOLUME)": None,
                        "networks": ["pg_service_network"],
                    },
                    "pg_admin": {
                        "X-REF-FUNCT-TEMPLATE-PG-ADMIN(X-REF-PGADMIN-CONTAINER-NAME,X-REF-PGADMIN-ENV,X-REF-PGADMIN-PORTS,X-REF-PGADMIN-VOLUME)": None,
                        "networks": ["pg_service_network"],
                    },
                },
                "networks": {"pg_service_network": {"name": "pg_service_network"}},
            },
            ref_files={
                "templates/core.yml": _CORE_FILE,
                "templates/image_version.yml": _IMAGE_VERSION_FILE,
                "templates/postgres.yml": _POSTGRES_FILE,
                "templates/pg_admin.yml": _PG_ADMIN_FILE,
            },
        )

    def test_two_postgres_services_expand_correctly(self) -> None:
        self._setup_stack(
            {
                "X-REF-DB1-CONTAINER-NAME": "db1",
                "X-REF-DB1-ENV": [
                    "POSTGRES_DB=mydb1",
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                ],
                "X-REF-DB1-PORTS": [],
                "X-REF-DB1-VOLUME": ["./data/db1:/var/lib/postgresql"],
                "X-REF-DB2-CONTAINER-NAME": "db2",
                "X-REF-DB2-ENV": [
                    "POSTGRES_DB=mydb2",
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                ],
                "X-REF-DB2-PORTS": [],
                "X-REF-DB2-VOLUME": ["./data/db2:/var/lib/postgresql"],
                "X-REF-PGADMIN-CONTAINER-NAME": "pg_admin",
                "X-REF-PGADMIN-ENV": [
                    "PGADMIN_DEFAULT_EMAIL=admin@admin.com",
                    "PGADMIN_DEFAULT_PASSWORD=password",
                ],
                "X-REF-PGADMIN-PORTS": "8080:80",
                "X-REF-PGADMIN-VOLUME": [
                    "./data/pgadmin:/var/lib/pgadmin",
                ],
            }
        )
        self.generator.start(MockFileHelper.input_file)

        expected: dict[str, Any] = {
            "services": {
                "db-one": _postgres_service(
                    container="db1",
                    env_vars=[
                        "POSTGRES_DB=mydb1",
                        "POSTGRES_USER=user",
                        "POSTGRES_PASSWORD=password",
                    ],
                    ports=[],
                    volumes=["./data/db1:/var/lib/postgresql"],
                    network="pg_service_network",
                ),
                "db-two": _postgres_service(
                    container="db2",
                    env_vars=[
                        "POSTGRES_DB=mydb2",
                        "POSTGRES_USER=user",
                        "POSTGRES_PASSWORD=password",
                    ],
                    ports=[],
                    volumes=["./data/db2:/var/lib/postgresql"],
                    network="pg_service_network",
                ),
                "pg_admin": {
                    "image": "dpage/pgadmin4",
                    "container_name": "pg_admin",
                    "restart": "unless-stopped",
                    "environment": [
                        "PGADMIN_DEFAULT_EMAIL=admin@admin.com",
                        "PGADMIN_DEFAULT_PASSWORD=password",
                    ],
                    "ports": ["8080:80"],
                    "volumes": ["./data/pgadmin:/var/lib/pgadmin"],
                    "networks": ["pg_service_network"],
                    "security_opt": ["no-new-privileges:true"],
                    "pids_limit": 100,
                    "mem_limit": "512m",
                    "cpus": "1.0",
                },
            },
            "networks": {"pg_service_network": {"name": "pg_service_network"}},
        }
        self.verify_no_diff(expected)

    def test_base_template_env_merged_into_postgres_services(self) -> None:
        # TZ from base template must be prepended to each postgres service's env list
        self._setup_stack(
            {
                "X-REF-DB1-CONTAINER-NAME": "db1",
                "X-REF-DB1-ENV": ["POSTGRES_DB=mydb1", "POSTGRES_USER=user"],
                "X-REF-DB1-PORTS": [],
                "X-REF-DB1-VOLUME": ["./data/db1:/var/lib/postgresql"],
                "X-REF-DB2-CONTAINER-NAME": "db2",
                "X-REF-DB2-ENV": ["POSTGRES_DB=mydb2", "POSTGRES_USER=user"],
                "X-REF-DB2-PORTS": [],
                "X-REF-DB2-VOLUME": ["./data/db2:/var/lib/postgresql"],
                "X-REF-PGADMIN-CONTAINER-NAME": "pg_admin",
                "X-REF-PGADMIN-ENV": ["PGADMIN_DEFAULT_EMAIL=a@b.com"],
                "X-REF-PGADMIN-PORTS": "8080:80",
                "X-REF-PGADMIN-VOLUME": ["./data/pgadmin:/var/lib/pgadmin"],
            }
        )
        self.generator.start(MockFileHelper.input_file)
        output = self.mock_file_helper.get_output()
        assert output is not None

        db1_env = output["services"]["db-one"]["environment"]
        db2_env = output["services"]["db-two"]["environment"]

        assert db1_env[0] == "TZ=Asia/Singapore"
        assert "POSTGRES_DB=mydb1" in db1_env

        assert db2_env[0] == "TZ=Asia/Singapore"
        assert "POSTGRES_DB=mydb2" in db2_env

    def test_pgadmin_env_not_merged_with_base_template_env(self) -> None:
        # PgAdmin uses a scalar env arg, so BASE-TEMPLATE environment is overwritten —
        # TZ must NOT appear in pg_admin's environment (different from postgres services)
        self._setup_stack(
            {
                "X-REF-DB1-CONTAINER-NAME": "db1",
                "X-REF-DB1-ENV": ["POSTGRES_DB=mydb1"],
                "X-REF-DB1-PORTS": [],
                "X-REF-DB1-VOLUME": [],
                "X-REF-DB2-CONTAINER-NAME": "db2",
                "X-REF-DB2-ENV": ["POSTGRES_DB=mydb2"],
                "X-REF-DB2-PORTS": [],
                "X-REF-DB2-VOLUME": [],
                "X-REF-PGADMIN-CONTAINER-NAME": "pg_admin",
                "X-REF-PGADMIN-ENV": [
                    "PGADMIN_DEFAULT_EMAIL=admin@admin.com",
                    "PGADMIN_DEFAULT_PASSWORD=password",
                ],
                "X-REF-PGADMIN-PORTS": "8080:80",
                "X-REF-PGADMIN-VOLUME": [],
            }
        )
        self.generator.start(MockFileHelper.input_file)
        output = self.mock_file_helper.get_output()
        assert output is not None

        pg_admin_env = output["services"]["pg_admin"]["environment"]
        assert "TZ=Asia/Singapore" not in pg_admin_env
        assert "PGADMIN_DEFAULT_EMAIL=admin@admin.com" in pg_admin_env

    def test_postgres_ports_empty_list_when_not_exposed(self) -> None:
        # X-REF-DB-PORTS: [] must resolve to an empty ports list (not a list with None)
        self._setup_stack(
            {
                "X-REF-DB1-CONTAINER-NAME": "db1",
                "X-REF-DB1-ENV": ["POSTGRES_DB=mydb1"],
                "X-REF-DB1-PORTS": [],
                "X-REF-DB1-VOLUME": [],
                "X-REF-DB2-CONTAINER-NAME": "db2",
                "X-REF-DB2-ENV": ["POSTGRES_DB=mydb2"],
                "X-REF-DB2-PORTS": [],
                "X-REF-DB2-VOLUME": [],
                "X-REF-PGADMIN-CONTAINER-NAME": "pg_admin",
                "X-REF-PGADMIN-ENV": ["PGADMIN_DEFAULT_EMAIL=a@b.com"],
                "X-REF-PGADMIN-PORTS": "8080:80",
                "X-REF-PGADMIN-VOLUME": [],
            }
        )
        self.generator.start(MockFileHelper.input_file)
        output = self.mock_file_helper.get_output()
        assert output is not None

        assert output["services"]["db-one"]["ports"] == []
        assert output["services"]["db-two"]["ports"] == []

    def test_image_versions_resolved_from_include_file(self) -> None:
        # image values must come from templates/image_version.yml, not literal strings
        self._setup_stack(
            {
                "X-REF-DB1-CONTAINER-NAME": "db1",
                "X-REF-DB1-ENV": ["POSTGRES_DB=mydb1"],
                "X-REF-DB1-PORTS": [],
                "X-REF-DB1-VOLUME": [],
                "X-REF-DB2-CONTAINER-NAME": "db2",
                "X-REF-DB2-ENV": ["POSTGRES_DB=mydb2"],
                "X-REF-DB2-PORTS": [],
                "X-REF-DB2-VOLUME": [],
                "X-REF-PGADMIN-CONTAINER-NAME": "pg_admin",
                "X-REF-PGADMIN-ENV": ["PGADMIN_DEFAULT_EMAIL=a@b.com"],
                "X-REF-PGADMIN-PORTS": "8080:80",
                "X-REF-PGADMIN-VOLUME": [],
            }
        )
        self.generator.start(MockFileHelper.input_file)
        output = self.mock_file_helper.get_output()
        assert output is not None

        assert output["services"]["db-one"]["image"] == "postgres:18.3-alpine"
        assert output["services"]["db-two"]["image"] == "postgres:18.3-alpine"
        assert output["services"]["pg_admin"]["image"] == "dpage/pgadmin4"

    def test_missing_include_file_raises_error(self) -> None:
        input_data: dict[str, Any] = {
            "X-OUTPUT": MockFileHelper.output_file,
            "X-INCLUDE": ["templates/core.yml", "templates/missing.yml"],
        }
        mock = MockFileHelper({MockFileHelper.input_file: input_data})
        mock.setup_ref_file("templates/core.yml", _CORE_FILE)
        generator = YamlGenerator(
            file_helper=mock,
            traverser=YamlTraverser(),
            multistage_actions=DefaultActions.get(),
        )
        with pytest.raises(ValueError, match="File does not exist"):
            generator.start(MockFileHelper.input_file)
