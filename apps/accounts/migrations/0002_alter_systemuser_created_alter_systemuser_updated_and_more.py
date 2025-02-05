# Generated by Django 5.1.4 on 2024-12-31 11:27

import common.db.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="systemuser",
            name="created",
            field=common.db.models.ForeignKey(
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="accounts_system_user_created",
                to=settings.AUTH_USER_MODEL,
                verbose_name="创建人",
            ),
        ),
        migrations.AlterField(
            model_name="systemuser",
            name="updated",
            field=common.db.models.ForeignKey(
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="accounts_system_user_updated",
                to=settings.AUTH_USER_MODEL,
                verbose_name="上次修改人",
            ),
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        default=common.db.models.generate_id,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_delete", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=255, verbose_name="部门名称")),
                (
                    "path",
                    models.CharField(
                        db_index=True, max_length=512, verbose_name="层级路径"
                    ),
                ),
                (
                    "created_name",
                    models.CharField(max_length=32, verbose_name="创建人姓名"),
                ),
                (
                    "updated_name",
                    models.CharField(
                        default="", max_length=32, verbose_name="上次修改人姓名"
                    ),
                ),
                (
                    "created",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_department_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="创建人",
                    ),
                ),
                (
                    "parent",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_department_parent",
                        to="accounts.department",
                        verbose_name="上级部门",
                    ),
                ),
                (
                    "updated",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_department_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="上次修改人",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="systemuser",
            name="department",
            field=common.db.models.ForeignKey(
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="accounts_system_user_department",
                to="accounts.department",
            ),
        ),
        migrations.CreateModel(
            name="Permission",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        default=common.db.models.generate_id,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_delete", models.BooleanField(default=False)),
                (
                    "code",
                    models.CharField(
                        db_index=True, max_length=64, verbose_name="权限编码"
                    ),
                ),
                ("name", models.CharField(max_length=128, verbose_name="权限名称")),
                (
                    "description",
                    models.CharField(
                        default="", max_length=256, verbose_name="权限描述"
                    ),
                ),
                (
                    "is_category",
                    models.BooleanField(default=False, verbose_name="是否为分类节点"),
                ),
                (
                    "created_name",
                    models.CharField(max_length=32, verbose_name="创建人姓名"),
                ),
                (
                    "updated_name",
                    models.CharField(
                        default="", max_length=32, verbose_name="上次修改人姓名"
                    ),
                ),
                (
                    "created",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_permission_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="创建人",
                    ),
                ),
                (
                    "parent",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_permission_parent",
                        to="accounts.permission",
                        verbose_name="上级权限",
                    ),
                ),
                (
                    "updated",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_permission_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="上次修改人",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        default=common.db.models.generate_id,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_delete", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=64, verbose_name="角色名称")),
                (
                    "description",
                    models.CharField(
                        default="", max_length=128, verbose_name="角色描述"
                    ),
                ),
                (
                    "created_name",
                    models.CharField(max_length=32, verbose_name="创建人姓名"),
                ),
                (
                    "updated_name",
                    models.CharField(
                        default="", max_length=32, verbose_name="上次修改人姓名"
                    ),
                ),
                (
                    "created",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_role_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="创建人",
                    ),
                ),
                (
                    "permission",
                    common.db.models.ManyToManyField(
                        db_constraint=False,
                        related_name="accounts_role_permission",
                        to="accounts.permission",
                        verbose_name="权限",
                    ),
                ),
                (
                    "updated",
                    common.db.models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounts_role_updated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="上次修改人",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="systemuser",
            name="role",
            field=common.db.models.ManyToManyField(
                db_constraint=False,
                related_name="accounts_system_user_role",
                to="accounts.role",
            ),
        ),
    ]
