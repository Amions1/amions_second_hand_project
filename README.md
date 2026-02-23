# 阿烽二手优品
基于 Django + Vue 的前后端分离二手商品交易系统。

## 技术栈
- 后端：Django, MySQL
- 前端：Vue 3, Element Plus 
- 其他：Redis, WebSocket, LangChain

## 运行步骤
1.  后端：
    ```bash
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```
2.  前端：
    ```bash
    npm install
    npm run dev
    ```