from __future__ import annotations

from stock_repo_brushup.models import LibraryRecommendation


CATALOG: dict[str, dict[str, str]] = {
    "yfinance": {
        "package": "yfinance",
        "category": "market-data",
        "reason": "価格データ取得の実装を軽量化できます。Yahoo Finance由来の履歴価格・銘柄情報をPythonから扱いやすくします。",
        "hint": "data_provider.py を分離し、download_prices(symbols, start, end) のような薄い関数に閉じ込めると置換しやすくなります。",
        "caution": "Yahoo Finance非公式APIを利用するOSSです。本番・商用用途では利用規約と代替データソースを確認してください。",
    },
    "ta": {
        "package": "ta",
        "category": "technical-analysis",
        "reason": "OHLCVからRSI、MACD、ボリンジャーバンドなどの特徴量をPandas上で生成しやすくなります。",
        "hint": "features/technical.py に add_technical_features(df) を追加し、既存のDataFrame処理に差し込む構成が安全です。",
        "caution": "指標を増やしすぎると過学習しやすいため、バックテストとウォークフォワード検証をセットで導入してください。",
    },
    "backtesting": {
        "package": "backtesting",
        "category": "backtest",
        "reason": "売買シグナルや戦略ロジックを、履歴データで再現性高く検証できます。",
        "hint": "strategies/ と backtests/ を分け、サンプル戦略を1つだけ追加してCIで最小データの実行確認をします。",
        "caution": "過去成績は将来の利益を保証しません。手数料、スリッページ、サバイバーシップバイアスを明記してください。",
    },
    "quantstats": {
        "package": "quantstats",
        "category": "performance-reporting",
        "reason": "リターン系列からSharpe、最大ドローダウン、月次ヒートマップなどの成績レポートを作れます。",
        "hint": "reports/performance.py を追加し、バックテスト結果のreturns SeriesからHTMLレポートを生成します。",
        "caution": "HTMLレポートのartifact化は便利ですが、実データや口座情報を公開repoへ含めないよう注意してください。",
    },
    "pyportfolioopt": {
        "package": "PyPortfolioOpt",
        "category": "portfolio-optimization",
        "reason": "平均分散最適化、リスクモデル、Black-Littermanなどのポートフォリオ配分機能を追加できます。",
        "hint": "portfolio/optimizer.py に optimize_weights(prices) を実装し、入出力をCSV/JSONで固定すると既存アプリへ組み込みやすいです。",
        "caution": "期待リターン推定に強く依存します。推定期間とリバランス頻度をREADMEへ明記してください。",
    },
    "skfolio": {
        "package": "skfolio",
        "category": "ml-portfolio-optimization",
        "reason": "scikit-learn風APIでポートフォリオ最適化、リスク管理、クロスバリデーションを扱えます。",
        "hint": "MLパイプラインやモデル選択があるrepoでは、既存のsklearn構成に estimator として組み込むのが自然です。",
        "caution": "機能が豊富な分、単純な可視化repoには過剰な場合があります。まずサンプルnotebookか小さなCLIから導入してください。",
    },
    "openbb": {
        "package": "openbb",
        "category": "fundamental-data-platform",
        "reason": "複数の金融データプロバイダやファンダメンタル情報を統合する土台になります。",
        "hint": "providers/openbb_provider.py として隔離し、APIキーが必要なプロバイダは環境変数経由にします。",
        "caution": "依存関係が大きくなりやすいため、軽量repoではoptional extraとして導入してください。",
    },
}


def make_recommendation(key: str, priority: int) -> LibraryRecommendation:
    item = CATALOG[key]
    return LibraryRecommendation(
        key=key,
        package=item["package"],
        category=item["category"],
        priority=priority,
        reason=item["reason"],
        integration_hint=item["hint"],
        caution=item["caution"],
    )
