import json, os, tqdm
import psycopg2

# Define the database connection parameters
def connect_to_db(host, database, user, password, port=5432):
    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to execute a query and save results to a file
def get_code_pairs(connection, output_file):
    cursor = connection.cursor()
    # 8584153
    # 4,292,076
    j = 0
    i = 4234
    # end = 8584153//400
    end = 4234 * 4

    k = 0
    types = {
        "4":"clones.similarity_token >= 0.85 and clones.syntactic_type  = 3",
        "3":"clones.similarity_token < 0.85 and clones.syntactic_type  = 3",
        "2":"clones.syntactic_type = 2",
        "1":"clones.syntactic_type = 1",
    }

    amounts = {
        "0" : 0,
        "1" : 0,
        "2" : 0,
        "3" : 0,
        "4" : 0,
    }
    
    while j < end:
        # print(k + 1)
        query = f"SELECT clones.function_id_one AS function1_id, \
                clones.function_id_two AS function2_id, \
                    CASE \
                        WHEN clones.syntactic_type = 3 AND clones.similarity_token >= 0.85::double precision THEN 4 \
                        WHEN clones.syntactic_type = 3 AND clones.similarity_token < 0.85::double precision THEN 3 \
                        ELSE clones.syntactic_type \
                    END AS clonetype \
            FROM clones where {types[str(k+1)]} limit {i};"

        cursor.execute(query)
        print(f"getting {j}/{end} {(j/end)*100:.2f}%", end="\r")

        j += i

        rows = [dict(func1id=row[0], func2id=row[1], clonetype=row[2]) for row in cursor.fetchall()]
        # rows = [dict(func1id=row[0], func2id=row[1], clonetype=row[2]) for row in cursor.fetchall()]
        
        if not os.path.exists(output_file):
            with open(output_file, mode='a+', encoding="utf-8")  as f:
                f.write("[\n")

        with open(output_file, mode='a+', encoding="utf-8") as f:
            for r in rows:
                json.dump(r, f)
                f.write(",\n") 
                amounts[str(r["clonetype"])] += 1
        
        k = (k + 1) % 4
    
    print()
    j = 0
    i = 4234
    # end = 8584153//400
    end = 4234 * 4
    while j < end:
        query = f"SELECT false_positives.function_id_one AS function1_id, \
                false_positives.function_id_two AS function2_id  \
                FROM false_positives limit {i} offset {j};"

        cursor.execute(query)
        print(f"getting {j}/{end} {(j/end)*100:.2f}%", end="\r")

        rows = [dict(func1id=row[0], func2id=row[1], clonetype=0) for row in cursor.fetchall()]
        # rows = [dict(func1id=row[0], func2id=row[1], clonetype=row[2]) for row in cursor.fetchall()]
        
        if not os.path.exists(output_file):
            with open(output_file, mode='a+', encoding="utf-8")  as f:
                f.write("[\n")

        with open(output_file, mode='a+', encoding="utf-8") as f:
            for r in rows:
                json.dump(r, f)
                f.write(",\n")
                amounts["0"] += 1
        j += i
    
    with open(output_file, mode='a+', encoding="utf-8")  as f:
        f.write("\n]")

    print()
    print(json.dumps(amounts))
    print(f"Query results saved to {output_file}")

    cursor.close()

def get_code_from_pairs(connection, pair_file, output_file):
    cursor = connection.cursor()
    with open(pair_file, "r") as f:
        clone_id = json.load(f)

    resultant = {}
    for pairs in tqdm.tqdm(clone_id):
        function1 = pairs["func1id"]
        function2 = pairs["func2id"]

        q = f"SELECT f.text, f.function_id \
             from pretty_printed_functions f \
        where f.function_id = {function1}"

        cursor.execute(q)
        code = cursor.fetchall()
        # if code[-1][1] != function1:
        #     print(code[-1][1], function1)
        # print(len(code))
        if code:
            resultant[function1] = code[0][0].replace("\n", "")
        # print(resultant)

        q = f"SELECT f.text \
             from pretty_printed_functions f \
        where f.function_id = {function2}"

        cursor.execute(q)
        code = cursor.fetchall()
        # print(len(code))
        if code:
            resultant[function2] = code[0][0].replace("\n", "")

    with open("code_segments_int.json", "w+") as f:
        json.dump(resultant, f)


def make_test_train_valid(clone_id):
    import random
    with open(clone_id, "r") as f:
        data = json.load(f)
    random.shuffle(data)

    split = int(len(data) * 0.9)

    train = data[:split]
    test = data[split:]

    print("entire dataset: ", len(data))
    print("train dataset: ", len(train))
    print("test dataset: ", len(test))
    
    with open("train_pairs.json", "w+") as f:
        json.dump(train, f)
    with open("test_pairs.json", "w+") as f:
        json.dump(test, f)


if __name__ == "__main__":
    # Database configuration
    db_config = {
        "host": "",
        "database": "",
        "user": "",
        "password": "POSTGRES-Password",
        "port": 5433
    }

    output_file = "clones_ids.json"

    # Connect to the database
    connection = connect_to_db(**db_config)

    if connection:
        get_code_pairs(connection, output_file)
        get_code_from_pairs(connection, output_file, "code_segments.json")
        make_test_train_valid(output_file)

        connection.close()
