# main/management/commands/seed_products.py
from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Product

PRODUCTS = [
    'シェル','リアホルダーLR','レセプタクル','ブロックLR','Vブロック','テーブル900',
    'テンションベース','ボディKD','ボディHP','ボディHBX','ボディTWI','インディックス',
    'ベッドL＝1000','ベッドL＝1500','ベッドL＝2000','ベッドL＝2500','ベッドL＝3000',
    'ベッドL＝2000（両端面加工）','ジョウブフレーム','インアウトフィードフレーム',
    'フィードフレーム','フレーム','JSW100大物','JSW100小物','JSW130大物','JSW130小物',
    'JSW180大物','JSW180小物','1300クロスリンク','1300タンリンク','220ｔカドウバンウエ',
    '220ｔカドウバンシタ','220ｔコテイバン','JT70カドウバンウエ','JT70カドウバンシタ',
    'JT70カコテイバン','JSW素材','自社トラック積み込み','コンテナ積み荷おろし',
    'JSW100出荷','JSW130出荷','JSW180出荷','ターンテーブル','事務','その他',
]

class Command(BaseCommand):
    help = "Seed products (idempotent)"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        created = 0
        for name in PRODUCTS:
            _, was_created = Product.objects.get_or_create(name=name.strip())
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"done (created: {created})"))
