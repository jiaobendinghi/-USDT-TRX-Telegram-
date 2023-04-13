import aiosqlite
import os.path



class Database:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "data.db")
        self.db_name = db_path

    async def create_table(self, table_name: str, columns: list) -> None:
        """创建一个拥有给定名称和列的新表格。

        Args:
            table_name (str): 表格的名称。
            columns (list of str): 列名列表，每个元素为一个列名和数据类型组合的字符串。

        Raises:
            Exception: 如果出现任何错误，则抛出异常。

        # Examples:
        #     >>> db = Database('example.db')
        #     >>> await db.create_table('users', ['id INTEGER', 'name TEXT', 'age INTEGER'])

        """
        async with aiosqlite.connect(self.db_name) as db:
            # 将所有列名和数据类型连接成一条 SQL 语句，并在数据库上执行该语句。
            await db.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
            await db.commit()

    async def insert_record(self, table_name: str, values: tuple) -> int:
        """在指定的表中插入新记录，并指定对应列的值列表。

        Args:
            table_name (str): 表格的名称。
            values (tuple): 要插入的值列表。

        Returns:
            int: 新插入记录的 rowid。

        Raises:
            Exception: 如果出现任何错误，则抛出异常。

        # Examples:
        #     >>> db = Database('example.db')
        #     >>> rowid = await db.insert_record('users', (1, 'Peter', 27))
        #     >>> print(rowid)
        #     1

        """
        async with aiosqlite.connect(self.db_name) as db:
            try:
                await db.execute(
                    f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(values))})",
                    values)
                await db.commit()
                return True
            except Exception as e:
                await db.rollback()
                raise e

    async def update_record(self, table_name: str, column_name: str, new_value: any, condition: str):
        """更新满足条件的表中现有记录中的某一列的值。

        Args:
            table_name (str): 表格的名称。
            column_name (str): 要更新的列名。
            new_value (any): 要更新的新值。
            condition (str): 更新条件。

        Returns:
            int: 受影响行数。

        Raises:
            Exception: 如果出现任何错误，则抛出异常。

        # Examples:
        #     >>> db = Database('example.db')
        #     >>> num_rows = await db.update_record('users', 'age', 28, 'name=?', ('Peter',))
        #     >>> print(num_rows)
        #     1

        """
        async with aiosqlite.connect(self.db_name) as db:
            try:
                print(f"UPDATE {table_name} SET {column_name} = ? WHERE {condition}")
                cursor = await db.execute(
                    f"UPDATE {table_name} SET {column_name} = ? WHERE {condition}",
                    (new_value,))
                await db.commit()
                #return cursor.rowcount
            except Exception as e:
                await db.rollback()
                raise e

    async def delete_record(self, table_name: str, condition: str, values: tuple = ()) -> int:
        """删除满足条件的表中现有记录。

        Args:
            table_name (str): 表格的名称。
            condition (str): 删除条件。
            values (tuple, optional): 删除条件的值列表。默认为空元组。

        Returns:
            int: 受影响行数。

        Raises:
            Exception: 如果出现任何错误，则抛出异常。

        # Examples:
        #     >>> db = Database('example.db')
        #     >>> num_rows = await db.delete_record('users', 'name=?', ('Peter',))
        #     >>> print(num_rows)
        #     1

        """
        async with aiosqlite.connect(self.db_name) as db:
            try:
                cursor = await db.execute(f"DELETE FROM {table_name} WHERE {condition}", values)
                await db.commit()
                return cursor.rowcount
            except Exception as e:
                await db.rollback()
                raise e

    async def select_one_record_condition(self, table_name: str, condition: str, values: tuple = ()) -> dict:
        """从指定表格中检索符合条件条件的单条记录。

        Args:
            table_name (str): 表格的名称。
            condition (str): 查询条件。
            values (tuple, optional): 查询条件的值列表。默认为空元组。

        Returns:
            dict: 包含符合条件的单条记录的字典。如果未找到匹配项，则返回空字典。

        Raises:
            Exception: 如果出现任何错误，则抛出异常。

        # Examples:
        #     >>> db = Database('example.db')
        #     >>> record = await db.select_one_record('users', 'name=?', ('Peter',))
        #     >>> print(record)
        #     {'id': 1, 'name': 'Peter', 'age': 28}

        """
        async with aiosqlite.connect(self.db_name) as db:
            try:
                cursor = await db.execute(f"SELECT * FROM {table_name} WHERE {condition}", values)
                result = await cursor.fetchone()
                # 将列名和对应的值组成一个字典，并将其作为查询结果返回。
                return dict(zip([description[0] for description in cursor.description], result)) if result else {}
            except Exception as e:
                raise e

    async def select_all_records_condition(self, table_name: str, condition: str, values: tuple = ()) -> dict:
        """从指定表格中检索所有记录。

        Args:
            table_name (str): 表格的名称。

        Returns:
            list of dict: 包含所有记录的列表，每个记录都是一个包含列名和对应值的字典。

        Raises:
            Exception: 如果出现任何错误，则抛出异常。

        Examples:
            # >>> db = Database('example.db')
            # >>> records = await db.select_all_records('users')
            # >>> print(records)
            # [{'id': 1, 'name': 'Peter', 'age': 28}, {'id': 2, 'name': 'Alice', 'age': 21}]

        """
        async with aiosqlite.connect(self.db_name) as db:
            try:
                cursor = await db.execute(f"SELECT * FROM {table_name} WHERE {condition}", values)
                #cursor = await db.execute(f"SELECT * FROM {table_name}")
                results = await cursor.fetchall()
                # 将每行数据转换成一个字典，并将它们添加到结果列表中。
                return [dict(zip([description[0] for description in cursor.description], row)) for row in results]
            except Exception as e:
                raise e

    async def select_all_records(self, table_name: str) -> list:
        """从指定表格中检索所有记录。

        Args:
            table_name (str): 表格的名称。

        Returns:
            list of dict: 包含所有记录的列表，每个记录都是一个包含列名和对应值的字典。

        Raises:
            Exception: 如果出现任何错误，则抛出异常。

        Examples:
            # >>> db = Database('example.db')
            # >>> records = await db.select_all_records('users')
            # >>> print(records)
            # [{'id': 1, 'name': 'Peter', 'age': 28}, {'id': 2, 'name': 'Alice', 'age': 21}]

        """
        async with aiosqlite.connect(self.db_name) as db:
            try:
                cursor = await db.execute(f"SELECT * FROM {table_name}")
                results = await cursor.fetchall()
                # 将每行数据转换成一个字典，并将它们添加到结果列表中。
                return [dict(zip([description[0] for description in cursor.description], row)) for row in results]
            except Exception as e:
                raise e

    async def close_connection(self) -> None:
        """关闭与数据库的连接。"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.close()


if __name__ == '__main__':
    #     >>> db = Database('example.db')
    #     >>> await db.create_table('users', ['id INTEGER', 'name TEXT', 'age INTEGER'])
    import asyncio


    async def main():
        db = Database()
        record = await db.select_all_records('transfer')
        print(record)
        # await db.close_connection()


    asyncio.run(main())


