#!/usr/bin/env python
"""
Backpack Exchange 做市交易程序統一入口
支持命令行模式和面板模式
"""
import argparse
import sys
import os

# 嘗試導入需要的模塊
try:
    from logger import setup_logger
    from config import API_KEY, SECRET_KEY
except ImportError:
    API_KEY = os.getenv('API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    def setup_logger(name):
        import logging
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger

# 創建記錄器
logger = setup_logger("main")

def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='Backpack Exchange 做市交易程序')
    
    # 模式選擇
    parser.add_argument('--panel', action='store_true', help='啟動圖形界面面板')
    parser.add_argument('--cli', action='store_true', help='啟動命令行界面')
    
    # 基本參數
    parser.add_argument('--api-key', type=str, help='API Key (可選，默認使用環境變數或配置文件)')
    parser.add_argument('--secret-key', type=str, help='Secret Key (可選，默認使用環境變數或配置文件)')
    
    # 做市參數
    parser.add_argument('--symbol', type=str, help='交易對 (例如: SOL_USDC)')
    parser.add_argument('--spread', type=float, help='價差百分比 (例如: 0.5)')
    parser.add_argument('--quantity', type=float, help='訂單數量 (可選)')
    parser.add_argument('--max-orders', type=int, default=3, help='每側最大訂單數量 (默認: 3)')
    parser.add_argument('--duration', type=int, default=3600, help='運行時間（秒）(默認: 3600)')
    parser.add_argument('--interval', type=int, default=60, help='更新間隔（秒）(默認: 60)')

    return parser.parse_args()

def main():
    """主函數"""
    args = parse_arguments()
    
    # 優先使用命令行參數中的API密鑰
    api_key = args.api_key or API_KEY
    secret_key = args.secret_key or SECRET_KEY
    
    # 檢查API密鑰
    if not api_key or not secret_key:
        logger.error("缺少API密鑰，請通過命令行參數或環境變量提供")
        sys.exit(1)
    
    # 決定執行模式
    if args.panel:
        # 啟動圖形界面面板
        try:
            from panel.panel_main import run_panel
            run_panel(api_key=api_key, secret_key=secret_key, default_symbol=args.symbol)
        except ImportError as e:
            logger.error(f"啟動面板時出錯，缺少必要的庫: {str(e)}")
            logger.error("請執行 pip install rich 安裝所需庫")
            sys.exit(1)
    elif args.cli:
        # 啟動命令行界面
        try:
            from cli.commands import main_cli
            main_cli(api_key, secret_key)
        except ImportError as e:
            logger.error(f"啟動命令行界面時出錯: {str(e)}")
            sys.exit(1)
    elif args.symbol and args.spread is not None:
        # 如果指定了交易對和價差，直接運行做市策略
        try:
            from strategies.market_maker import MarketMaker
            
            # 初始化做市商
            market_maker = MarketMaker(
                api_key=api_key,
                secret_key=secret_key,
                symbol=args.symbol,
                base_spread_percentage=args.spread,
                order_quantity=args.quantity,
                max_orders=args.max_orders
            )
            
            # 執行做市策略
            market_maker.run(duration_seconds=args.duration, interval_seconds=args.interval)
            
        except KeyboardInterrupt:
            logger.info("收到中斷信號，正在退出...")
        except Exception as e:
            logger.error(f"做市過程中發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    else:
        # 沒有指定執行模式時顯示幫助
        print("請指定執行模式：")
        print("  --panel   啟動圖形界面面板")
        print("  --cli     啟動命令行界面")
        print("  直接指定  --symbol 和 --spread 參數運行做市策略")
        print("\n使用 --help 查看完整幫助")

if __name__ == "__main__":
    main() 