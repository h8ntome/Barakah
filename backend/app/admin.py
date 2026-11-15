"""Provision administrator roles through trusted server access only."""
import argparse
from sqlalchemy import select
from .db import SessionLocal
from .models import User


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('email')
    parser.add_argument('--revoke', action='store_true')
    args = parser.parse_args()
    with SessionLocal.begin() as db:
        user = db.scalar(select(User).where(User.email == args.email.lower()))
        if user is None:
            parser.error('User must register before role provisioning')
        user.is_admin = not args.revoke
    print('Administrator role updated')


if __name__ == '__main__':
    main()
