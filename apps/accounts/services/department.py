from typing import Optional

from accounts.models import Department, SystemUser
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone


class DepartmentService:
    TREE_KEY = "accounts:department_tree"
    TREE_KEY_TIMEOUT = 60 * 60 * 24

    @staticmethod
    def name_exists(
        name: str,
        parent: Optional[Department] = None,
        instance: Optional[Department] = None,
    ) -> bool:
        queryset = Department.objects.filter(name=name)
        if parent:
            queryset = queryset.filter(parent=parent)
        if instance:
            queryset = queryset.exclude(id=instance.id)
        return queryset.exists()

    @classmethod
    @transaction.atomic
    def create(
        cls, department_data, created: Optional[SystemUser] = None
    ) -> Department:
        parent = department_data.get("parent", None)
        department = Department.objects.create(
            name=department_data["name"],
            parent=parent,
            created=created,
            created_name=created.nickname if created else "",
        )
        if parent:
            department.path = f"{parent.path}/{department.id}"
        else:
            department.path = str(department.id)
        department.save(update_fields=("path",))

        cls.delete_cache()
        return department

    @classmethod
    @transaction.atomic
    def update(
        cls,
        instance: Department,
        department_data,
        updated: Optional[SystemUser] = None,
    ) -> Department:
        new_parent = department_data.get("parent", instance.parent)
        old_path = instance.path

        instance.name = department_data["name"]
        instance.parent = new_parent
        instance.updated = updated
        instance.updated_name = updated.nickname if updated else ""

        if new_parent:
            instance.path = f"{new_parent.path}/{instance.id}"
        else:
            instance.path = str(instance.id)
        instance.save()

        if old_path != instance.path:
            # 父部门发生变化, 递归更新子部门的 path
            cls._update_descendants_path(instance, old_path)

        cls.delete_cache()

        return instance

    @staticmethod
    def _update_descendants_path(instance: Department, old_path: str):
        descendants = Department.objects.filter(path__startswith=f"{old_path}/")
        for descendant in descendants:
            descendant.path = descendant.path.replace(old_path, instance.path, 1)
        Department.objects.bulk_update(descendants, ["path"])

    @classmethod
    @transaction.atomic
    def soft_delete(cls, instance: Department, deleted: Optional[SystemUser] = None):
        sub_departments = Department.objects.filter(path__startswith=instance.path)
        sub_departments.update(
            is_delete=True,
            updated_at=timezone.now(),
            updated=deleted,
            updated_name=deleted.nickname if deleted else "",
        )

        cls.delete_cache()

    @staticmethod
    def all():
        return Department.objects.all().order_by("-id")

    @classmethod
    def get_by_id(cls, pk: int) -> Optional[Department]:
        try:
            instance = Department.objects.get(id=pk)
        except Department.DoesNotExist:
            return None

        return instance

    @classmethod
    def get_tree_cached(
        cls, parent_id: Optional[int] = None, force_refresh: bool = False
    ):
        """
        获取部门树形结构，支持缓存
        :param parent_id: 父部门 ID
        :param force_refresh: 是否强制刷新缓存
        :return: 树形结构的部门数据
        """
        # 强制刷新缓存或首次查询

        if force_refresh or not cache.exists(cls.TREE_KEY):
            tree = cls._build_tree()
            cache.set(cls.TREE_KEY, tree, timeout=cls.TREE_KEY_TIMEOUT)
        else:
            tree = cache.get(cls.TREE_KEY)

        # 返回整个树或子树
        if parent_id:
            return cls._get_sub_tree(tree, parent_id)
        return tree

    @staticmethod
    def _build_tree():
        """
        构建完整的部门树（不直接暴露）
        :return: 树形结构
        """
        departments = Department.objects.all().order_by("id")
        department_dict = {
            dept.id: {
                "id": dept.id,
                "name": dept.name,
                "path": dept.path,
                "children": [],
            }
            for dept in departments
        }

        tree = []
        for dept in departments:
            if dept.parent_id:
                department_dict[dept.parent_id]["children"].append(
                    department_dict[dept.id]
                )
            else:
                tree.append(department_dict[dept.id])

        return tree

    @staticmethod
    def _get_sub_tree(tree, parent_id):
        """
        获取子树
        :param tree: 完整的树形结构
        :param parent_id: 父节点 ID
        :return: 子树
        """
        for node in tree:
            if node["id"] == parent_id:
                return node["children"]
            sub_tree = DepartmentService._get_sub_tree(node["children"], parent_id)
            if sub_tree:
                return sub_tree
        return None

    @classmethod
    def delete_cache(cls):
        """
        清除缓存
        """
        cache.delete(cls.TREE_KEY)
