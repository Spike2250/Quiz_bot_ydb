import ast
import random
import json
from prettytable import PrettyTable

from quiz_bot.database import pool, execute_select_query, execute_update_query
from quiz_bot.questions import quiz_data


async def get_quiz_index(user_id):
    query = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(
        pool, query,
        user_id=user_id
    )
    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]


async def update_quiz_index(user_id, question_index):
    query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPSERT INTO `quiz_state` (
            `user_id`,
            `question_index`)
        VALUES ($user_id, $question_index);
    """
    execute_update_query(
        pool, query,
        user_id=user_id,
        question_index=question_index,
    )


async def update_user_name(user_id, user_name):
    query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $user_name AS Utf8;
        
        UPSERT INTO `quiz_state` (
            `user_id`,
            `user_name`)
        VALUES ($user_id, $user_name);
    """
    execute_update_query(
        pool, query,
        user_id=user_id,
        user_name=user_name,
    )


async def get_question_order(user_id):
    query = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_order
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(
        pool, query,
        user_id=user_id
    )
    if len(results) == 0:
        return []
    if results[0]["question_order"] is None:
        return []
    return ast.literal_eval(results[0]["question_order"])


async def update_question_order(user_id, order):
    query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_order AS Utf8;

        UPSERT INTO `quiz_state` (
            `user_id`,
            `question_order`)
        VALUES ($user_id, $question_order);
    """
    execute_update_query(
        pool, query,
        user_id=user_id,
        question_order=str(order),
    )


async def get_current_score(user_id):
    query = f"""
        DECLARE $user_id AS Uint64;

        SELECT current_score
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(
        pool, query,
        user_id=user_id
    )
    if len(results) == 0:
        return 0
    if results[0]["current_score"] is None:
        return 0
    return results[0]["current_score"]


async def update_current_score(user_id, score):
    query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $current_score AS Uint64;

        UPSERT INTO `quiz_state` (
            `user_id`,
            `current_score`)
        VALUES ($user_id, $current_score);
    """
    execute_update_query(
        pool, query,
        user_id=user_id,
        current_score=score,
    )


async def get_top_score(user_id):
    query = f"""
        DECLARE $user_id AS Uint64;

        SELECT top_score
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(
        pool, query,
        user_id=user_id
    )
    if len(results) == 0:
        return 0
    if results[0]["top_score"] is None:
        return 0
    return results[0]["top_score"]


async def update_top_score(user_id, score):
    query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $top_score AS Uint64;

        UPSERT INTO `quiz_state` (
            `user_id`,
            `top_score`)
        VALUES ($user_id, $top_score);
    """
    execute_update_query(
        pool, query,
        user_id=user_id,
        top_score=score,
    )


async def get_records_table() -> str:
    def create_table(results):
        table = PrettyTable()
        fields = ['Место', 'Игрок', 'Счет']
        table.field_names = fields

        for i, unit in enumerate(results):
            table.add_row([
                i + 1,
                unit['user_name'],
                unit['top_score']
            ])
        return str(table)

    query = f"""
        SELECT user_name, top_score
        FROM `quiz_state`
        ORDER BY top_score DESC
        LIMIT 10;
    """
    results = execute_select_query(
        pool, query,
    )
    return create_table(results)


def save_question_to_ydb(question):
    query = f"""
        DECLARE $id AS Uint64;
        DECLARE $question AS Json;

        UPSERT INTO `quiz_questions` (
            `id`,
            `question`)
        VALUES ($id, $question);
    """
    execute_update_query(
        pool, query,
        id=question['id'],
        question=json.dumps(question),
    )


def write_questions_to_ydb():
    for q in quiz_data:
        save_question_to_ydb(q)


async def get_questions(limit=100):
    query = f"""
        SELECT question
        FROM `quiz_questions`
        LIMIT {limit};
    """
    results = execute_select_query(
        pool, query
    )
    if len(results) == 0:
        return []
    if results[0]["question"] is None:
        return []

    upd_results = []
    for unit in results:
        upd_results.append(
            json.loads(unit["question"])
        )
    return upd_results


async def get_question_list(shuffle: bool = False, number: int | None = None) -> dict:
    data = await get_questions()
    if not data:
        write_questions_to_ydb()
        data = await get_questions()

    if shuffle:
        random.shuffle(data)
    if number and number <= len(data):
        data = data[:number]
    return {
        'list': data,
        'index_list': [x['id'] for x in data]
    }


async def get_question(id_):
    query = f"""
        DECLARE $id AS Uint64;

        SELECT question
        FROM `quiz_questions`
        WHERE id == $id;
    """
    results = execute_select_query(
        pool, query, id=id_
    )
    if len(results) == 0:
        return {}
    if results[0]["question"] is None:
        return {}
    return json.loads(results[0]["question"])


async def create_question_list_from_indexes(index_list):
    result = []
    for index in index_list:
        result.append(
            await get_question(index)
        )
    return result
