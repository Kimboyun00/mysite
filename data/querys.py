create_query = """
    CREATE TABLE IF NOT EXISTS`user_info`
    (
        `id` varchar(32) primary key, 
        `password` varchar(32) not null, 
        `name` varchar(16)
    )
"""
# 로그인 쿼리 
login_query = """
    SELECT * FROM `user_info` WHERE `id` = %s AND `password` = %s
"""
# 회원 가입 쿼리 
signup_query = """
    INSERT INTO `user_info` VALUES (%s, %s, %s)
"""
# 아이디 중복 체크 쿼리 
check_query = """
    SELECT * FROM `user_info` WHERE `id` = %s
"""