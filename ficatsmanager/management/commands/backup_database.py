import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

if TYPE_CHECKING:  # pragma: no cover
    import dropbox  # noqa: F401


class Command(BaseCommand):
    help = (
        "Genera un respaldo de la base de datos configurada en settings.py y lo sube "
        "a Dropbox."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--local-only",
            action="store_true",
            help="Genera el respaldo pero omite la carga a Dropbox.",
        )

    def handle(self, *args, **options):
        db_settings = settings.DATABASES.get("default") or {}
        engine = db_settings.get("ENGINE", "")

        if not engine:
            raise CommandError("No existe una configuración de base de datos válida.")

        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        db_name_hint = db_settings.get("NAME") or "database"
        db_label = Path(db_name_hint).stem or "database"

        with tempfile.TemporaryDirectory() as tmp_dir:
            backup_path = Path(tmp_dir) / f"{db_label}_{timestamp}.sql"

            if "mysql" in engine:
                self.stdout.write("Creando volcado MySQL…")
                self._dump_mysql(db_settings, backup_path)
            elif engine.endswith("sqlite3"):
                self.stdout.write("Respaldando archivo SQLite…")
                backup_path = self._copy_sqlite(db_settings, Path(tmp_dir), timestamp)
            else:
                raise CommandError(
                    f"Motor de base de datos no soportado para respaldo automático: {engine}"
                )

            if options["local_only"]:
                final_path = Path.cwd() / backup_path.name
                shutil.copy2(backup_path, final_path)
                self.stdout.write(self.style.SUCCESS(f"Respaldo guardado en {final_path}"))
                return

            access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
            if not access_token:
                raise CommandError(
                    "Define la variable de entorno DROPBOX_ACCESS_TOKEN para subir el respaldo."
                )

            dropbox_folder = os.getenv("DROPBOX_BACKUP_FOLDER", "/vet_arce_backups").strip()
            if not dropbox_folder:
                dropbox_folder = "/"
            if not dropbox_folder.startswith("/"):
                dropbox_folder = f"/{dropbox_folder}"
            if dropbox_folder != "/":
                dropbox_folder = dropbox_folder.rstrip("/")

            destination = f"{dropbox_folder}/{backup_path.name}" if dropbox_folder != "/" else f"/{backup_path.name}"

            self.stdout.write(f"Subiendo respaldo a Dropbox ({destination})…")
            self._upload_to_dropbox(access_token, backup_path, destination)
            self.stdout.write(self.style.SUCCESS("Respaldo subido correctamente a Dropbox."))

    def _dump_mysql(self, db_settings, backup_path: Path) -> None:
        name = db_settings.get("NAME")
        user = db_settings.get("USER")
        password = db_settings.get("PASSWORD", "")
        host = db_settings.get("HOST") or "localhost"
        port = str(db_settings.get("PORT") or "3306")

        if not all([name, user]):
            raise CommandError("Faltan credenciales MySQL (NAME y USER son obligatorios).")

        mysqldump_bin = os.getenv("MYSQLDUMP_PATH", "mysqldump")

        cmd = [
            mysqldump_bin,
            f"-h{host}",
            f"-P{port}",
            f"-u{user}",
            name,
        ]

        env = os.environ.copy()
        if password:
            env["MYSQL_PWD"] = password

        with backup_path.open("wb") as output:
            result = subprocess.run(
                cmd,
                check=False,
                stdout=output,
                stderr=subprocess.PIPE,
                env=env,
                text=False,
            )

        if result.returncode != 0:
            stderr = result.stderr.decode() if result.stderr else ""
            raise CommandError(
                "Fallo al ejecutar mysqldump. Verifica que esté instalado y las credenciales sean válidas.\n"
                + stderr
            )

    def _copy_sqlite(self, db_settings, tmp_dir: Path, timestamp: str) -> Path:
        db_path = Path(db_settings.get("NAME") or "")
        if not db_path.exists():
            raise CommandError(f"La base de datos SQLite no existe: {db_path}")

        destination = tmp_dir / f"{db_path.stem}_{timestamp}{db_path.suffix or '.sqlite3'}"
        shutil.copy2(db_path, destination)
        return destination

    def _upload_to_dropbox(self, access_token: str, backup_path: Path, destination: str) -> None:
        try:
            import dropbox
            from dropbox.exceptions import ApiError, AuthError
            from dropbox.files import WriteMode

            client = dropbox.Dropbox(access_token)
            with backup_path.open("rb") as backup_file:
                client.files_upload(
                    backup_file.read(),
                    destination,
                    mode=WriteMode("overwrite"),
                    mute=True,
                )
        except ImportError as exc:  # pragma: no cover - dependerá del entorno de ejecución real
            raise CommandError(
                "El paquete 'dropbox' es obligatorio. Ejecuta 'pip install -r requirements.txt'."
            ) from exc
        except AuthError as exc:
            raise CommandError("Token de Dropbox inválido o expirado.") from exc
        except ApiError as exc:
            raise CommandError(f"Dropbox rechazó la carga: {exc}") from exc