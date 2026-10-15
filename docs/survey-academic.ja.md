# SREエージェント／AIOps 学術サーベイ
[English](survey-academic.md) | **日本語** · [概要](../README.ja.md)

調査基準日：2026-10-11。対象：既存AIツールを活用し、AWS・Azure・GCPで段階的にSRE検証を行うための研究選定。

## 結論

最初に比較すべきなのは「どのモデルが最強か」より、診断用データ、ツール、役割分担、変更権限、成功判定をどう揃えるかである。

- **読取中心の比較**：Cloud-OpsBench、OpenRCA。既存エージェントを同じ証拠・予算で比較しやすい。
- **実環境での修復比較**：AIOpsLab、ITBench、SREGym。診断の文章と、実際の回復を分けて採点する。
- **既製の研究エージェント候補**：STRATUS、各ベンチマークの参照エージェント、既存の汎用コーディングエージェント。最初から独自フレームワークを開発する必要はない。
- **安全性の必読**：STRATUSの可逆操作の前提、AIOpsDoomのテレメトリ攻撃、失敗過程を分析する2026年論文。人間の承認画面だけでは十分とはいえない。
- **マルチクラウドへの外挿は未検証**：Kubernetes上の成功は、AWS/Azure/GCP固有のIAM、課金、管理API、マネージドDBまで扱える証明ではない。

以下の「示唆」「推奨」は本サーベイの判断であり、論文が商用本番運用を保証しているという意味ではない。ソフトウェア、クラスタ、障害注入、課金APIは今回実行していない。

## 1. 読み分けるための評価地図

| 評価の種類 | 主な論文／資産 | 確認できること | それだけでは確認できないこと |
|---|---|---|---|
| 障害記録・テレメトリのオフライン診断 | OpenRCA、RCAgent、RCACopilot | 証拠抽出、原因候補、説明、分析コード | 変更後の回復、操作の副作用 |
| 同一スナップショットとの対話 | Cloud-OpsBench | ツール選択と証拠収集を条件固定して比較 | 動的な環境変化、実修復 |
| 生きた環境への障害注入 | AIOpsLab、ITBench | 読取・操作・回復のループ | 全クラウド・全障害への一般化 |
| ノイズ・複合障害を含む実行環境 | SREGym | 誤誘導、低層障害、再発する障害への対応 | 実企業の全運用制約 |
| エージェント構造の比較 | mABC、STRATUS、LATS-RCA、RCLAgent | 役割分担、探索、復旧機構の効果 | エージェント数だけによる品質保証 |
| 安全性・失敗過程の検証 | AI Oops、Why Do AI Agents…、Between Promise and Pain | 誤解釈、情報脱落、攻撃・副作用 | 未知の全攻撃や全副作用への保証 |

研究間の成功率は、タスク、モデル世代、データ、ツール、制限時間、採点方法が違う。横並びの順位表にしない。

## 2. 中核論文

### 2.1 AIOpsLab：障害ライフサイクルを試す基盤

**Chen et al., AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds**

- 公開：2025-01-12。MLSys 2025。前身の設計論文は2024-07-16。
- 手法：Agent-Cloud Interfaceを介して、アプリ配備、負荷生成、障害注入、テレメトリ、エージェント評価を統合。
- 評価：DeathStarBenchのHotelReservation／SocialNetwork、48問題。検知、局所化、原因分析、軽減を分ける。
- 限界：小規模の既知アプリ・障害群。タスク別の成功を、そのまま連続した本番対応の成功率に読み替えない。
- 示唆：既存AIチームのツール接続を比較する実験台に適する。クラウド固有の障害は別途追加する。

一次資料：[論文](https://arxiv.org/abs/2501.06706)、[MLSys版](https://proceedings.mlsys.org/paper_files/paper/2025/file/d1f9e4a9f109b6e8b75ed362736f22ec-Paper-Conference.pdf)、[公式実装](https://github.com/microsoft/AIOpsLab)、[前身論文](https://arxiv.org/abs/2407.12165)。

### 2.2 ITBench：SRE・セキュリティ・コストを分離して評価

**Jha et al., ITBench: Evaluating AI Agents across Diverse Real-World IT Automation Tasks**

- 公開：2025-02-07。ICML 2025。
- 手法：Kubernetes上の実務由来シナリオ、参照エージェント、診断・軽減の採点。
- 評価：初期94シナリオはSRE・CISO・FinOpsの合計。本文のSRE実験は42シナリオ。GPT-4oの診断pass@1は13.81%、軽減は11.43%。
- 限界：論文当初の公開サブセットと全評価セットは異なる。13.8%という要旨の数値を修復成功率と呼ばない。現行リポジトリやITBench-AAの結果とも区別する。
- 示唆：既製SREエージェントと比較する基準に使える。成功、誤変更、時間、費用を別々に記録する。

一次資料：[論文・Table 4/Appendix C](https://arxiv.org/html/2502.05352v1)、[IBMの出版情報](https://research.ibm.com/publications/itbench-evaluating-ai-agents-across-diverse-real-world-it-automation-tasks)、[公式実装](https://github.com/itbench-hub/ITBench)。

### 2.3 OpenRCA：大量テレメトリからの分析能力

**Xu et al., OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?**

- 公開：ICLR 2025論文。公式プロジェクトの採択告知は2025-01-23。初回投稿の正確な公開日は今回未確認。
- 手法：自然言語の課題に対し、ログ・メトリクス・トレースをPython等で分析。参照実装RCA-agentを提供。
- 評価：3システム、335障害、68GB超のテレメトリ。論文時点の最良モデルClaude 3.5でも完全解決は11.34%。
- 限界：原因・時刻等を当てるオフライン課題。ライブ修復のベンチマークではない。
- 示唆：複数の既存AIツールで、分析担当とコード実行担当の受け渡しを検証しやすい。モデル名より分析環境と入力条件の固定が重要。

一次資料：[ICLR論文ページ](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d29b8d53678015079e1d245c023e49d2-Abstract-Conference.html)、[公式実装](https://github.com/microsoft/OpenRCA)、[公式プロジェクト](https://microsoft.github.io/OpenRCA/)。

### 2.4 Cloud-OpsBench：正解と証拠充足を分ける

**Wang et al., Cloud-OpsBench: A Reproducible Benchmark for Agentic Root Cause Analysis in Cloud Systems**

- 初版：2026-02-28。参照版：v2、2026-08-22。プレプリント。
- 手法：実クラスタで障害を確認してスナップショット化。診断ツールへの同一応答を再生し、証拠の到達点も採点する。
- 評価：Online Boutique／Train-Ticket、57故障種、754事例。最良Joint RCA Accuracyは0.76／0.68だが、対応するEvidence Closure Rateは0.38／0.15。
- 限界：有限の収録済みクエリだけに対応。状態変更・ライブ修復を評価しない。
- 示唆：本件の最初の候補。異なる既製AIに同じ証拠を与え、原因名を当てただけの回答を見抜ける。

一次資料：[論文v2](https://arxiv.org/html/2603.00468v2)、[公開日履歴](https://arxiv.org/abs/2603.00468)、[公式実装・配布物](https://github.com/LLM4Ops/Cloud-OpsBench)。

### 2.5 SREGym：複雑な障害と汎用エージェントの比較

**Clark et al., SREGym: A Live Benchmark for AI SRE Agents with High-Fidelity Failure Scenarios**

- 初版：2026-05-08。参照版：v3、2026-07-30。プレプリント。
- 手法：実クラウドネイティブ環境に、異なる層の故障、無関係なノイズ、相関障害、準安定障害を構成。
- 評価：90問題。STRATUSに加えClaude Code、Codex等を比較し、診断と実際の軽減を検証する。
- 限界：診断側にはLLM judgeも使う。採点モデルの影響と実状態の検証を分ける必要がある。
- 示唆：既存AIチームを丸ごと評価しやすい。まずLite版、次に複合障害へ。論文の90問題全体と現行コードを同一視せず、版を固定する。

一次資料：[論文v3](https://arxiv.org/html/2605.07161v3)、[公開日履歴](https://arxiv.org/abs/2605.07161)、[公式実装](https://github.com/SREGym/SREGym)。

### 2.6 STRATUS：役割分離とUndoを実装した研究エージェント

**Chen et al., STRATUS: A Multi-agent System for Autonomous Reliability Engineering of Modern Clouds**

- 初版：2025-05-27。NeurIPS 2025。参照版：2026-03-19、v2。
- 手法：検知・診断・軽減・Undoを状態機械で制御。Transactional Non-Regression（TNR）を定式化。
- 評価：AIOpsLab／ITBenchで軽減成功を比較。既存法に対する改善を報告。
- 限界：TNRは書込の排他性、正確なUndo、操作列長の上限を前提とする。保証対象はトランザクション境界の状態で、途中の一時悪化は許す。一般的な外部APIを無条件に元へ戻せる証明ではない。
- 示唆：自作前に試す有力候補。マルチAIでは同時書込を制限し、Undo不能操作を別扱いにする。

一次資料：[論文v2・§3–4](https://arxiv.org/html/2506.02009v2)、[NeurIPS版](https://papers.nips.cc/paper_files/paper/2025/file/47a6e9e2c3019f13ad94a0f259fe4970-Paper-Conference.pdf)、[公式実装](https://github.com/xlab-uiuc/stratus)。

### 2.7 RCAgent：内部モデル、ツール、文脈管理

**Wang et al., RCAgent: Cloud Root Cause Analysis by Autonomous Agents with Tool-Augmented Large Language Models**

- 初版：2023-10-25。参照版：2024-08-02、v3。CIKM 2024採択。
- 手法：内部配備モデル、情報収集・分析ツール、観測の参照キー、動作軌跡の自己整合性集約。
- 評価：Alibaba CloudのFlink基盤の診断・問題発見。原因、解決案、証拠、責任範囲を評価し、ReActを上回ると報告。
- 限界：産業固有のツールと非公開データへの依存が大きい。提案解決策の品質と自動実行の安全性は別。
- 示唆：ローカル／内部モデルを活かす設計の参考。複数エージェントに全文ログを繰り返し渡すより、証拠の識別子と必要箇所を共有する。

一次資料：[論文v3](https://arxiv.org/html/2310.16340v3)、[書誌・公開履歴](https://arxiv.org/abs/2310.16340)。

### 2.8 mABC：専門役割と投票

**Zhang et al., mABC: Multi-Agent Blockchain-inspired Collaboration for Root Cause Analysis in Micro-Services Architecture**

- 初版：2024-04-18。Findings of EMNLP 2024、2024-11。
- 手法：7専門エージェント、工程を定めるAgent Workflow、ブロックチェーンに着想を得た投票。循環依存による無限探索を制限。
- 評価：AIOps challengeとTrain-Ticketのデータ。構成要素の除去実験も行う。
- 限界：投票は独立した外部検証と同義ではない。同じ誤った証拠を共有するエージェントは合意して誤る可能性がある。
- 示唆：役割分担の比較候補。投票数、トークン費用、単一エージェントとの差分を揃えて測る。

一次資料：[ACL論文・ソフトウェア](https://aclanthology.org/2024.findings-emnlp.232/)、[全文](https://arxiv.org/html/2404.12135)、[著者のコード](https://github.com/zwpride/mABC)。

### 2.9 LATS-RCA：仮説の木探索と実運用との差

**Naakka, Wang, Mäntylä, LATS-RCA: Language Agent Tree Search for Root Cause Analysis in Microservices**

- 初版：2026-05-05。参照版：2026-06-12、v2。SEAA 2026採択。
- 手法：複数エージェントがログ・メトリクスを調べ、反省評価で根本原因仮説の木を探索する。
- 評価：公開LO2で91.3%。Zoner Oyの実運用事例では複数試行平均65.1%。
- 限界：公開の単純な構成と、本番の複数要因・観測不足で差がある。製品横断の成功率ではない。
- 示唆：マルチAIは仮説の幅を増やすために使う。探索の深さ・時間・費用を制限し、不十分な証拠では保留できるようにする。

一次資料：[論文v2](https://arxiv.org/html/2605.03505v2)、[公開日・採択情報](https://arxiv.org/abs/2605.03505)、[再現パッケージ](https://github.com/kottinov/lats-rca)。

### 2.10 RCLAgent：トレース構造に沿った並列診断

**Zhang et al., Towards In-Depth Root Cause Localization for Microservices with Multi-Agent Recursion-of-Thought**

- 公開：2026-05-14。プレプリント。関連する2025版は2025-08-28公開。
- 手法：トレースのspanごとに専用エージェントを割り当て、再帰・並列に診断し、全体証拠グラフを合成。
- 評価：AIOPS 2022、Augmented-TrainTicket、RCAEvalで局所化精度と推論効率を比較。
- 限界：主題は原因局所化。独立した変更権限、承認、ロールバックの有効性まではこの結果で判断できない。
- 示唆：AWS担当／Azure担当という固定分担だけでなく、実サービス依存関係に沿う分担を検討する。ただし診断用構造と実行権限の構造は分ける。

一次資料：[2026論文全文](https://arxiv.org/html/2605.14866v1)、[関連する2025論文](https://arxiv.org/abs/2508.20370)、[論文記載のコード](https://github.com/LLM4AIOps/RCLAgent-V2)。

### 2.11 Between Promise and Pain：失敗を設計材料にする

**Cornacchia et al., Between Promise and Pain: The Reality of Automating Failure Analysis in Microservices with LLMs**

- 公開：APSys 2025、2025-10（会議2025-10-12〜13）。
- 手法：ReAct単体とAutoGenのreasoner／executor／criticを比較し、専門ツールの影響も検証。
- 評価：AIOpsLabを拡張したSocialNetwork／HotelReservation、性能障害や健全な状態を含む。
- 限界・発見：誤検知、過信、誤ったAPIの反復、不要な変更を観察。マルチエージェント化の効果は条件依存。
- 示唆：「障害なし」「既に自然回復済み」を必須の負例にする。失敗時に停止・訂正・人間へ引継ぎできるかを測る。

一次資料：[著者公開PDF](https://mcanini.github.io/papers/kashef2.apsys25.pdf)、[DOI](https://doi.org/10.1145/3725783.3764388)。

### 2.12 Why Do AI Agents Systematically Fail…：受け渡し品質の効果

**Kim et al., Why Do AI Agents Systematically Fail at Cloud Root Cause Analysis?**

- 初版：2026-02-10。参照版：2026-03-04、v2。プレプリント。
- 手法・評価：OpenRCAで5モデル、1,675実行を分析。推論、エージェント間通信、環境操作の12失敗型を分類。
- 発見：データの誤解釈と探索不足が共通。生成コード、実行結果、例外を共有する通信改善で、通信関連の失敗を最大15ポイント減少。
- 限界：改善実験はBank部分集合が中心。全エージェント構造に同じ効果を保証しない。
- 示唆：担当者間には要約だけを渡さず、実行結果と証拠参照を添える。独立検証器やメモリ制限も比較対象にする。

一次資料：[論文v2](https://arxiv.org/html/2602.09937v2)、[公開履歴](https://arxiv.org/abs/2602.09937)。

### 2.13 OpenRCA 2.0：因果経路の採点

**Fang et al., OpenRCA 2.0: From Outcome Labels to Causal Process Supervision**

- 初版：2026-06-25。参照版：2026-06-30、v2。work in progressと明記。
- 手法：既知の障害注入から影響を前向きに検証するPAVEで、因果伝播経路を付与。
- 評価：3系統のアプリ、500事例、11モデル。根本原因集合の完全一致は平均20.7%。一部原因を当てる評価とは大きく異なる。
- 限界：合成障害から選別したデータ。本文付録は採択後の公開を予告する一方、プロジェクトサイトには2.0結果がある。データ一式・版の対応確認を再現前の条件にする。
- 示唆：原因名だけでなく、原因→中間異常→ユーザー症状の証拠付き説明を要求する設計に役立つ。

一次資料：[論文v2・Appendix A](https://arxiv.org/html/2606.27154v2)、[公開履歴](https://arxiv.org/abs/2606.27154)、[プロジェクトサイト](https://microsoft.github.io/OpenRCA/)。

### 2.14 When AIOps Become “AI Oops”：観測データも信頼境界の外

**Pasquini et al., When AIOps Become “AI Oops”: Subverting LLM-driven IT Operations via Telemetry Manipulation**

- 初版：2025-08-08。USENIX Security 2026、2026-08。
- 手法：AIOpsDoomでテレメトリ由来の誘導を評価し、構造を利用して入力を浄化するAIOpsShieldを提案。
- 評価：隔離したAIOpsLab環境、ReAct／Flash、GPT-4o／GPT-4.1等。もっともらしい誤った修復案へ誘導できることを示す。
- 限界：防御の実験結果は評価条件内のもの。未知の攻撃をすべて遮断する保証ではない。
- 示唆：ログ・トレース中の外部由来文字列を操作指示として扱わない。提案を読取証拠と照合し、権限検査はLLMの外で行う。人間向け要約にも証拠への参照が必要。

一次資料：[USENIX会議ページ](https://www.usenix.org/conference/usenixsecurity26/presentation/pasquini)、[確定版PDF](https://www.usenix.org/system/files/usenixsecurity26-pasquini.pdf)、[初版履歴](https://arxiv.org/abs/2508.06394)、[著者実装](https://github.com/RSAC-Labs/AIOpsDoom)。

### 2.15 宣言的マルチエージェント：読取専用でも価値を測る

**Adatiya & Kariya, A Declarative Multi-Agent Framework for Reducing On-Call Operational Burden**

- 公開：Google Research掲載2026年。正確な月日・査読会議は掲載情報から未確認。
- 手法：専門家記述の調査手順をmanager／workerが実行。ツール層で手順を検証し、読取専用・監査記録・RAGを組み合わせる。
- 評価：単一組織の複数サービス・地域。高重大度のトリアージ中央値を約30分から5分未満へ短縮と報告。
- 限界：対照的なユーザー実験なし。サンプル規模・公開再現物が十分示されず、強い一般化は避ける。修復は人間に残している。
- 示唆：初期の本番接続は診断支援から始める、という比較案の参考。設計例として扱い、効果量を目標値に転用しない。

一次資料：[Google Research掲載](https://research.google/pubs/a-declarative-multi-agent-framework-for-reducing-on-call-operational-burden/)、[著者PDF](https://storage.googleapis.com/gweb-research2023-media/pubtools/1046157.pdf)。

## 3. 歴史的に重要な補助資料

### RCACopilot

Chen et al., **Automatic Root Cause Analysis via Large Language Models for Cloud Incidents**。初版2023-05-25、EuroSys 2024刊行2024-04-22。アラートごとの既存ハンドラで情報収集し、類似インシデントを使って原因カテゴリを推定する。Microsoftの1年分の障害で最大0.766を報告。既存運用知識を活かす点が重要だが、非公開の組織固有データであり、その値は任意のクラウドに適用できない。「情報収集部が4年以上稼働」と「LLM全体が4年以上本番修復」は区別する。[論文](https://arxiv.org/abs/2305.15778)、[著者PDF](https://tianyin.github.io/pub/rca-copilot.pdf)、[大学の刊行記録](https://experts.illinois.edu/en/publications/automatic-root-cause-analysis-via-large-language-models-for-cloud/)。

### 初期の大規模な原因・軽減案推薦

Ahmed et al., **Recommending Root-Cause and Mitigation Steps for Cloud Incidents using Large Language Models**。2023-01-10初版、ICSE 2023。Microsoftの40,000件超のインシデントで、zero-shot／fine-tuning／multi-taskを比較し、担当者にも評価を依頼。推薦文の有用性と実システムを安全に修復する能力の違いを理解する入口になる。[論文](https://arxiv.org/abs/2301.03797)、[Microsoftの研究紹介](https://www.microsoft.com/en-us/research/blog/large-language-models-for-automatic-cloud-incident-management/)。

## 4. 再現可能性と既製資産の選び方

以下は2026-10-11に確認した公式READMEに基づく。リポジトリは更新されるため、実施時にcommit、依存lockfile、コンテナdigestを固定する。公開されていることと、そのまま安全に実行できることは別である。

| 資産 | 確認できた条件 | 本件での扱い |
|---|---|---|
| [Cloud-OpsBench](https://github.com/LLM4Ops/Cloud-OpsBench) | 754事例のスナップショット、参照エージェント、過程ラベル。ライブKubernetes不要。Streamable HTTPのMCPとCodex／OpenCode接続例あり | 最初の読取専用比較候補。接続と採点の実動確認は未実施 |
| [OpenRCA](https://github.com/microsoft/OpenRCA) | Python 3.10以上。公式推奨RAM32GB、空き80GB。データは別配布。時刻はUTC+8 | 端末容量確認後。正解ファイルをエージェントの可読範囲から除く |
| [AIOpsLab](https://github.com/microsoft/AIOpsLab/blob/main/README.md) | Python 3.11以上、Helm、Poetry/pip。kindまたはremote K8s。Azure VM用配備手順あり | 制御clientとLinux実行面を分ける。OSごとの互換性は未検証 |
| [SREGym](https://github.com/SREGym/SREGym) | Python 3.12以上、Docker、Helm4以上、kubectl、uv。Liteは17問題、kindで8vCPU/16GBが目安 | 初期の生きた環境の候補。全問題にはLinuxノードのSSH/rootが必要。managed K8sはそのままでは不可 |
| [STRATUS](https://github.com/xlab-uiuc/stratus/blob/main/README.md) | Python 3.12、CrewAI、K8s、モデル接続。AIOpsLab／ITBenchとの手順 | 研究参照実装。READMEの旧名・submodule参照を含め、採用前の整合確認が必要 |
| [ITBench](https://github.com/itbench-hub/ITBench) | 自己ホスト用資産とホスト型評価を区別。論文の全94件が初期公開コードに含まれるわけではない | まずローカル公開サブセット。登録・結果送信は別途判断 |
| [ITBench旧SRE Agent](https://github.com/itbench-hub/ITBench-SRE-Agent) | archiveされ、統合エージェントへの移行案内あり | 古い名前を固定採用しない。移行先と対応するシナリオ版を確認 |

SREGymのノード権限要件は大きな差である。EKS／AKS／GKEの管理面まで含む通常のマネージド環境と、クラウドVM上の自己管理Kubernetesは、別の実験レーンにする。OSレベル障害を試す場合、検証専用VM・クラスタ以外にroot権限を与えない。

Cloud-OpsBenchの再生物は最初に全クラスタを作らなくてよいため、ローカル環境から既存AIを比較する目的に合う。Linux／WSL2／VMのどれで実行するかは、端末資源と対象資産の依存関係を確認して決める。これらは推奨構成であり、特定端末での実機検証結果ではない。

## 5. マルチAI・マルチクラウド検証への落とし込み

### 5.1 設計を決める前の最小比較

下記は構造の効果を切り分けるための一般的な実験案。今回の具体的な実施順は[構成・検証計画](architecture-and-validation-plan.ja.md)を優先し、既存AI単体の接続確認、別AIの独立比較、同一modelでの役割追加の順に必要性を判断する。最初から全組合せを実施する必要はない。

1. **同一既存AI、同一モデル、同一ツール**で単体構成を測る。
2. 同じ条件で「調査担当＋証拠確認担当」を追加する。
3. 既存の参照エージェントを同じ制限時間・モデル予算で測る。
4. 効果のあった構造だけについて、別モデル／別プロバイダへ入れ替える。
5. 読取専用を合格したものに限り、検証用クラスタで承認付き修復を試す。

複数モデルを使うこと、複数エージェントを使うこと、複数クラウドを操作することは別変数にする。全部を同時に変えると、成功・失敗の原因を説明できない。

### 5.2 記録する指標

| 軸 | 記録内容 |
|---|---|
| 診断 | 原因コンポーネント、故障機構、影響範囲、時刻、複数原因集合の一致 |
| 証拠 | 各主張が参照するデータID・クエリ・時刻。反証の探索、未確認事項、誤引用 |
| 修復 | 実際のSLO回復、設定差分、持続的回復、別サービスの悪化、再発 |
| 安全性 | 禁止操作の要求／実行、未承認操作、対象クラウド・アカウントの取り違え、権限逸脱 |
| 復元 | ロールバックが完了したか、元状態との一致、途中悪化の大きさと時間 |
| 運用負担 | 人間の確認時間、承認待ち、差戻し、調査の重複、エスカレーション品質 |
| 費用 | モデル入力・出力、ツール呼出、再試行、クラウド資源費、総所要時間 |
| 再現性 | 複数試行のばらつき、モデル版、judge版、ノイズseed、初期状態の差 |

「alertが消えた」「LLM judgeが正解と言った」「エージェントが完了と報告した」のどれか一つだけを成功条件にしない。ベンチマーク基盤や正解データにアクセスして評価を回避する行動も、成功から除外する。

### 5.3 必須の失敗・安全シナリオ

- 障害なし、古いアラート、既に自然回復済み
- ログ不足、トレースの欠損、時刻ずれ、矛盾する観測
- 同じ原因からの多発アラートと、無関係な同時障害
- 最初に見つかったもっともらしい異常が原因ではないケース
- 変更後に別のSLOが悪化するケース
- 承認待ちの間に状態が変わり、提案が古くなるケース
- 同じクラスタへの二つのAIの競合変更
- アカウント／subscription／project／region／namespaceの取り違え
- テレメトリに含まれる外部文字列が、承認・変更を促すケース
- ツールのエラー、部分成功、API timeout、同一操作の再試行

攻撃耐性は、まず安全な合成データを用いた読取専用テストで確認する。公開システムへの攻撃、第三者の環境での障害注入、攻撃用コードの実行はこの計画の初期段階には含めない。

### 5.4 承認と安全境界の案

以下は研究の主張ではなく、本件向けの運用提案である。

- 調査エージェントは読取専用IDで動かす。診断文に実行権限を持たせない。
- 変更候補は、対象、根拠、差分、影響範囲、復元手順、検証条件、有効期限を持つ提案として出力する。
- 承認された操作と対象だけを実行層へ渡す。承認後に差分が変わった場合は再確認する。
- 変更は資源単位で排他。担当AIが複数でも、同じ資源への書込を同時に走らせない。
- ロールバック可能性を操作ごとに分類する。外部送信、課金、資格情報、破壊的データ操作を「Undo可能」と仮定しない。
- 独立した状態検証で回復を判定する。元の提案者だけに自己採点させない。
- 停止、時間・費用上限、監査記録はモデルのプロンプトだけに依存させない。

### 5.5 クラウド横断で追加すべき試験

文献の共通Kubernetes試験に加え、各クラウド固有のID・権限モデル、APIの遅延／部分失敗、クォータ、マネージドサービス、ネットワーク境界、監査ログを別表で評価する。三社の同名に見える機能を等価と仮定しない。

最初は同じアプリの同じ障害を一社ずつ再現し、ツールの戻り値を共通の証拠形式へ変換する。次に「クラウド間の依存」を加える。三社同時の自動修復は、単一クラウドでの承認・復元・監査が成立してから検討する。

## 6. 本サーベイで未確定の点

- 現行商用SRE製品のサポート範囲・価格・一般提供状況は[製品・技術者発表・実装調査](survey-products-and-practice.ja.md)を参照。
- 公開研究実装のWindowsネイティブ互換性、エンドツーエンド実行、API費用は未測定。
- OpenRCA 2.0の論文版と配布データの完全な対応は未検証。初期採用の必須依存にしない。
- 一部論文の本番データや社内ツールは非公開で、完全再現できない。
- 論文時点の数値は当時の構成の結果。2026年の別モデルや現行READMEの結果へ置き換えて解釈しない。
- 精度・時間の改善は、法的責任、SLA、セキュリティ認証、商用本番の安全保証にはならない。

## 推奨する読む順序

1. AIOpsLab、ITBench：何を評価するか
2. Cloud-OpsBench、OpenRCA：同一証拠でどう比較するか
3. STRATUS：変更と復元の境界
4. AI Oops、Why Do AI Agents…：壊れる経路と防御
5. SREGym：現実的な複雑さへの拡張
6. mABC、LATS-RCA、RCLAgent：既存構成で足りない場合の設計選択肢

この順序なら、広いサーベイを踏まえつつ、独自の巨大なマルチエージェント基盤を先に作ることを避けられる。
