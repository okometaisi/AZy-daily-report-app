# charts.py
import matplotlib.pyplot as plt
import io
import base64

def generate_task_pie_chart(task_summary):
    labels = []
    sizes = []

    for task_data in task_summary:
        if 'task' in task_data:
            labels.append(task_data['task'])
            total_minutes = task_data['total_duration_hour'] * 60 + task_data['total_duration_minute']
            sizes.append(total_minutes)

    if sizes:
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("タスク別の作業時間")

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = string.decode('utf-8')
        plt.close()
        return uri
    else:
        return None
