# マルチAI・マルチクラウド SRE エージェント調査

[English](README.en.md)

既存のSREエージェント、クラウド技術者の発表・実装事例、学術研究を調べ、AWS・Azure・GCPを対象とする段階的な検証構成を整理した資料集です。

**調査基準日：2026-10-11。状態：文献・公開コードの調査と設計提案。実験・導入・クラウド操作・API課金は未実施。**

## 最初に読むもの

| 順番 | 資料 | 内容 |
| --- | --- | --- |
| 1 | [製品・技術者発表・実装事例](docs/survey-products-and-practice.ja.md) | OpenAI公式例、Azure SRE Agent、AWS DevOps Agent、Gemini Cloud Assist、HolmesGPT等。提供状態、権限、費用、ライセンスと選定理由 |
| 2 | [学術サーベイ](docs/survey-academic.ja.md) | 中核15本＋補助2本。RCA、再生型benchmark、live repair、multi-agent、安全性と再現条件 |
| 3 | [構成・最小検証計画](docs/architecture-and-validation-plan.ja.md) | 共通証拠、既存AIの比較、承認と実行の分離、初回1ケース、実クラウドへの移行条件 |

## 調査から得た結論

- 最初から3クラウドに多数の自律agentを置かず、既存AI 1つの診断を基準にする。
- 同じ証拠・時間・費用上限で別AIを独立比較し、役割追加の効果を後から測る。
- 原因名の正解と、十分な証拠を集めたことを別に採点する。
- 調査、修復提案、人の承認、限定実行、実際の復旧確認を分ける。
- OSS、trial、read-onlyという名称だけで、全体無料や無変更を仮定しない。

Microsoftの細分化agent間引継ぎの失敗経験、Mary KayのAWS＋Azure実装、Google SREの承認付き操作、Datadogの再生型評価を照合しています。製品説明と顧客自己報告、デモ、査読研究、プレプリントの違いは各資料に記載しています。

## 推奨する初回実験

**Cloud-OpsBenchの公開snapshot 1件を、既存のMCP対応AI 1つで診断する。**

| 項目 | 提案する範囲 |
| --- | --- |
| 対象 | Online Boutique runtime/1。公開例のため動作確認として扱う |
| 構成 | 既製MCP server＋既存AI client。実Kubernetes／cloud credentialsは不要 |
| 上限 | 1run、診断5分、tool最大20回。推論費用の上限は実行前に確定 |
| 分離 | 正解label、golden trajectory、過去run、実cloud toolsをagentから隔離 |
| 評価 | 接続、原因component、fault type、引用、証拠不足、操作境界、停止、再現記録 |
| 代替 | 接続条件が合わなければHolmesGPT CLIの合成ファイル診断を検討 |

参照commitは[`ea05dafb`](https://github.com/LLM4Ops/Cloud-OpsBench/tree/ea05dafbc87b5985df8721622d63d4229c2b4224)。[MCP仕様](https://github.com/LLM4Ops/Cloud-OpsBench/blob/ea05dafbc87b5985df8721622d63d4229c2b4224/cloudopsbench_mcp/README.md)を確認した計画であり、このリポジトリで実動を確認したものではありません。serverにLLM keyが不要でも、clientの推論料金は別です。

## 全体構成

```text
公開snapshot／cloud別read-only取得
                ↓
共通証拠（出典・時刻・対象・欠損）
                ↓
単体診断AI ── 同条件の別AIを独立比較
                ↓
根拠確認 → 人の承認 → 限定実行
                ↓
独立したSLI・実状態検証 → cleanup・費用照合
```

論理上の責務を示したもので、各箱を常駐サービスとして新設する計画ではありません。同じ資源への変更は単一writerに限定し、承認後の状態変化、API timeout、不可逆操作を別途扱います。

## この資料で証明していないこと

- 製品やモデルの総合ランキング、本番の安全性、SLA
- 診断の文章だけによる実修復成功
- Kubernetesでの結果からの全cloud管理APIへの一般化
- プロセス停止・資源不在・継続課金停止・後日請求一致の同一視
- 特定アカウントの利用資格、trial適格性、最終料金

実施時はPASS／FAIL／INCONCLUSIVE／NOT_RUNを使い分けます。未実行を成功にせず、承認待ちを技術的失敗として数えません。

## 出典と公開範囲

公式docs、公開repo、著者・登壇者の資料、論文へのリンクを各節に付けています。論文全文、第三者コード、private telemetry、credentials、個人端末のpath、非公開の運用記録は含めません。

第三者資料の著作権・ライセンスは各提供元に帰属します。[第三者資料の扱い](THIRD_PARTY_NOTICES.md)も参照してください。製品状態・料金・repoの内容は調査日以降に変わるため、実施前に再確認が必要です。
