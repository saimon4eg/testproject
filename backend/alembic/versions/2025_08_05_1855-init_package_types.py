from alembic import op

# revision identifiers, used by Alembic.
revision = 'init_package_types'
down_revision = '6207cf5a46e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем базовые типы посылок
    op.execute(
        "INSERT INTO package_types (id, name) VALUES "
        "(1, 'Одежда'), "
        "(2, 'Электроника'), "
        "(3, 'Разное')"
    )


def downgrade() -> None:
    # Удаляем базовые типы посылок
    op.execute("DELETE FROM package_types WHERE id IN (1, 2, 3)")
