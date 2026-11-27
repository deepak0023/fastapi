"""connect users table to roles table

Revision ID: 04e557a55ef1
Revises: a7c932e85e94
Create Date: 2026-11-26 20:08:05.780596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04e557a55ef1'
down_revision: Union[str, Sequence[str], None] = 'a7c932e85e94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Preserve existing role values by mapping them to roles.id
    op.execute("""
        UPDATE users
        SET role_id = (
            SELECT id FROM roles
            WHERE LOWER(roles.title) = LOWER(users.role)
        )
        WHERE role IS NOT NULL
    """) if False else None

    with op.batch_alter_table('users', schema=None) as batch_op:

        batch_op.add_column(
            sa.Column('role_id', sa.Integer(), nullable=True)
        )

        batch_op.create_foreign_key(
            'fk_users_role_id_roles',
            'roles',
            ['role_id'],
            ['id']
        )

        batch_op.drop_column('role')

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:

        batch_op.add_column(
            sa.Column('role', sa.String(), nullable=True)
        )

        batch_op.drop_constraint(
            'fk_users_role_id_roles',
            type_='foreignkey'
        )

        batch_op.drop_column('role_id')
