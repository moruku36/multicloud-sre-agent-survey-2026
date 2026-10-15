# SRE エージェント調査：製品・技術者発表・実装事例
[English](survey-products-and-practice.md) | **日本語** · [概要](../README.ja.md)

調査日 2026年10月11日
状態 公開一次資料の調査結果 導入と実測は未実行  
目的 製品 発表 実装事例と学術研究を照合し マルチAI・マルチクラウドの構成候補を選ぶ

## 1 結論

**推奨は、既存エージェント1つの診断から始め、共通証拠で別AIと比較し、効果のある役割分担だけを加える構成。** 初回はCloud-OpsBenchと既存AIの再生型診断、HolmesGPT CLIの合成ファイル診断は代替とする。実クラウドは必要になった1社から始め、AWS DevOps Agent／Azure SRE Agentを用途で選ぶ。3社に自律エージェントを置く構成を先に作る根拠は、今回の調査では得られなかった。

OpenAI公式に、2026年9月10日公開の「Build an SRE agent for incident response」がある。付属の合成障害を調べ、Slackでrollback承認を記録する実装例で、実rollbackは行わない。公開情報だけから、独立した完成済み運用サービスだとは断定しない。[OpenAI公式サンプル](https://developers.openai.com/cookbook/examples/agents_api/apps/sev_bot/readme)

サーベイで設計を変える主な点は四つ。

- ログを読むだけの初回評価に、Kubernetesや3社のLB・VMを新設する必要はない。
- 「read-only」「Review」「無料trial」は範囲を確認する。Bash、外部通知、監視設定、ログ照会料金まで自動的に安全・無料になるわけではない。
- 原因推定、承認フロー、実データ取得、実修復を別段階で評価する。デモが動いたことをSLO・復旧・課金停止の実証へ広げない。
- Microsoftの専門agent間引継ぎの失敗経験と、AWS／Googleの役割分担例は併存する。マルチAIは目的ではなく比較変数とし、証拠・予算を揃えて単体との差を測る。

今回は公開一次資料と公開コードの読取りのみ。導入、API実行、アカウント操作、外部問い合わせ、課金、クラウド操作は行っていない。

## 2 候補の位置付け

| 候補 | 提供状態と確認した版 | 対応範囲 | 初回の位置付け |
| --- | --- | --- | --- |
| OpenAI sev_bot | 2026-09-10公開の公式Cookbook例。基盤のAgents APIは同日にpublic beta | サンプルはGitHub・AWS・Slack。外部証拠は差替え可能 | 公式実装例。承認フローの確認向き |
| HolmesGPT | 0.43.0、2026-10-07、prerelease=false、CNCF Sandbox | ローカルファイル、Kubernetes、observability、各cloudのtoolset／MCP | file-only診断の代替候補 |
| Robusta Platform | 商用managed／enterprise self-hosted製品。単一のGA日・固定版は今回未確定 | HolmesGPTを核にUI、通知、アラート分類、継続調査 | チーム運用を試す段階。CLI初回には不要 |
| Azure SRE Agent | 2025-05-19 preview、2026-03-10 GA | Azure中心。MCP・AWS DevOps Agent連携を公式発表 | Azureネイティブ運用の比較候補 |
| AWS DevOps Agent | 2025-12-02 preview、2026-03-31 GA | AWS、Azure、on-prem。接続元と権限に依存 | managedのマルチクラウド調査本命 |
| CloudWatch investigations | 2024-12-03 preview、2025-06-24 GA | AWSのmetrics・logs・traces・変更イベント | 既存AWS環境の単発診断baseline |
| Gemini Cloud Assist | 2026-10-07更新docsでPreview。proactive investigationsはprivate preview | GCP。investigationは単一project／App Hub application | 利用資格を確認する後段候補。無料ローカル試験には使わない |
| K8sGPT | v0.4.40、2026-10-09、prerelease=false | Kubernetes analyzerと任意のLLM説明 | 任意ログだけの初回からは除外 |

GAは全機能・全region・全accountでの提供保証ではない。AWS DevOps Agentのrelease managementは別機能でpreview。基盤のGAと混ぜない。モデルがAWS Bedrock／Azure／Vertexを使えることと、そのcloud資源を調査できることも別である。

一次資料：[Agents API changelog](https://developers.openai.com/api/docs/changelog)、[HolmesGPT release](https://github.com/HolmesGPT/holmesgpt/releases/tag/0.43.0)、[Robusta構成](https://docs.robusta.dev/master/how-it-works/oss-vs-saas.html)、[Azure GA](https://techcommunity.microsoft.com/blog/appsonazureblog/whats-new-in-azure-sre-agent-in-the-ga-release/4500779)、[AWS GA](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)、[CloudWatch GA](https://aws.amazon.com/about-aws/whats-new/2025/06/ga-accelerate-troubleshooting-amazon-cloudwatch-investigations/)、[K8sGPT release](https://github.com/k8sgpt-ai/k8sgpt/releases/tag/v0.4.40)。

## 3 各候補の権限 費用と採否

### OpenAI sev_bot

- **何なのか**：OpenAI公式Cookbookのコード例。Agents APIのsession、tool、記憶、webhook、承認を組み合わせる。基準コードはopenai-cookbookのcommit 5bd6cb40b6b84b69b2032d810610aa85064102df。独立した「SRE Agent」というmanaged製品のGAを、この例から読み取ることはできない。
- **権限**：付属evidence toolは読取り。rollbackは提案と承認の記録までで、deployment systemを呼ばない。GitHub／AWSのlive接続は任意設定。AWS skillsだけを入れてもAWSアクセス権は得られない。
- **必要な準備**：Python 3.14以上、uv、Docker等のsandbox、OpenAI API keyと別executor key、Slack app。双方向の承認には公開HTTPS callbackと署名検証の設定が必要。
- **ローカル試験**：データは付属fixtureにできる。ただしサンプル通りならOpenAI API呼出しとSlack投稿は本物。完全オフラインではない。
- **料金・ライセンス**：CookbookコードはMIT。OpenAIサービスの利用条件は別。modelは選択したAPI料金、toolは所定料金、OpenAI-hosted sandboxならcontainer料金。自前Dockerでもmodel APIが無料になるわけではない。実行総額と無料枠の適格性は未確認。
- **今回**：公式例の承認境界を評価する候補として採用。初回の再生型診断より準備が多いため、承認フローを評価する別枠。用途と必要な統合に応じて優先を決める。

根拠：[サンプル本文](https://developers.openai.com/cookbook/examples/agents_api/apps/sev_bot/readme)、[read-only toolと任意MCPの実装](https://github.com/openai/openai-cookbook/blob/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/agents_api/apps/sev_bot/tools.py)、[承認・cleanup実装](https://github.com/openai/openai-cookbook/blob/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/agents_api/apps/sev_bot/agent.py)、[MIT](https://github.com/openai/openai-cookbook/blob/5bd6cb40b6b84b69b2032d810610aa85064102df/LICENSE)、[Agents API料金の扱い](https://developers.openai.com/api/docs/guides/agents-api/overview)、[利用量の注意](https://developers.openai.com/api/docs/guides/agents-api/observability)。

### HolmesGPT

- **入力**：CLIのfile入力にログや公開runbookを渡せる。複数file、prompt-file、非対話1回実行、JSON応答保存をソースで確認。JSON保存は任意の診断schemaへの適合保証ではない。
- **対応範囲**：Kubernetes以外のVMやobservabilityを含め、AWS／Azure／GCPのtoolset／MCPがある。対応範囲は接続したtoolと権限に依存する。
- **安全上の注意**：利用可能なtoolsetを自動検出し、CLIは既存credentialsやkubeconfigを使い得る。Bashは既定有効。Kubernetes remediation MCPを足すとrestart・scale・patch等が可能になる。初回はこれらを使わない。
- **必要な認証**：ファイル診断だけならcloud認証は不要。外部LLMならそのproviderのAPI認証が必要。live接続を足すとAWS IAM／CLI、Azure RBAC／CLI、GCP IAM／gcloud・ADC等が必要になる。
- **料金・ライセンス**：0.43.0はApache-2.0。OSS利用料は不要だが、外部LLM、GPU／実行環境、接続先APIの料金は別。古い資料にあるMIT表記ではなく、採用タグのLICENSEを基準にする。
- **今回**：Cloud-OpsBenchと既存AIの接続条件が合わない場合の代替。実効tool無効化と隔離を確認し、合成ログ1件を診断する。live collectionや修復能力は対象外。

根拠：[CLI実装](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/main.py)、[ファイル追加](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/core/prompt.py)、[Apache-2.0](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/LICENSE)、[Bash](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/bash.md)、[Remediation MCP](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/kubernetes-remediation-mcp.md)、[AWS](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/aws.md)、[Azure](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/azure-mcp.md)、[GCP](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/gcp.md)。

### HolmesGPTを完全ローカルにできる条件

公式Ollama経路があり、ローカルOllamaにAPI keyは不要。ただしexperimentalで、tool callingが不安定な場合がある。モデルのlicense、RAM／VRAM、取得・実行環境は別確認が必要。[Ollama連携](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/ai-providers/ollama.md)

空のtoolsets設定は「全tool無効」の意味ではない。単一の全無効スイッチは確認できず、固定版の各toolsetをenabled:falseで上書きし、有効一覧を確認する必要がある。bash-always-denyも許可リスト外を拒否する設定で、すべてのBashを拒否する意味ではない。[toolset管理](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/core/toolset_manager.py)

max-stepsを1にすると最初のmodel呼出しからtoolsなしにするコード経路があるが、初期化や前提確認を抑止しない。したがって、これ単独では安全境界にできない。[呼出し実装](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/core/tool_calling_llm.py)

最小試験は、既存ホーム／認証を持たない隔離環境、ローカル推論以外のegress遮断、toolsets無効化、fallbackなしを条件とする。ここまでは資料とコードの確認であり、実機で動作を保証したものではない。条件を満たせなければ実行を保留する。

### Robusta Platform

HolmesGPTを中心とする管理層で、Web UI、Slack／Teams、背景調査、複数agentの管理を提供する。HolmesGPTと独立した推論エンジンとして二重に数えない。

商用Platformは無料で開始できるという案内があるものの、現行価格は見積方式で、無料件数・期間の確定値は取得できなかった。self-hosted Platformはenterprise plan。標準のin-cluster導入とPlatform accountを要するため、合成ファイルだけの初回には準備が増える。接続後の読取り・修復境界はHolmesのtool、RBAC、追加連携を含めて確認する。

公開repo robusta-dev/robustaは**Robusta Classic**というルールベースalert enrichment engineで、MIT、0.51.0。これを根拠に商用Platform全体がMIT・無料・ローカル配布だとは言わない。今回はCLIで診断価値が見えた後のチーム運用候補とする。

根拠：[OSSとSaaSの区別](https://docs.robusta.dev/master/how-it-works/oss-vs-saas.html)、[価格](https://home.robusta.dev/pricing)、[Classic](https://github.com/robusta-dev/robusta/blob/master/README.md)、[Classic release](https://github.com/robusta-dev/robusta/releases/tag/0.51.0)。

### Azure SRE Agent

Azureを中心に監視・調査・対応を行うmanaged製品。MCPとAWS DevOps Agent連携も公式発表されているが、これだけでGCPを含む全cloudに同じ修復能力があるとは判断しない。[GA](https://techcommunity.microsoft.com/blog/appsonazureblog/whats-new-in-azure-sre-agent-in-the-ga-release/4500779)、[AWS連携](https://techcommunity.microsoft.com/blog/appsonazureblog/announcing-aws-with-azure-sre-agent-cross-cloud-investigation-using-the-brand-ne/4507413)

- active Azure subscriptionが必要。作成者にはOwner、またはContributorとUser Access Administrator等が必要。agentはmanaged identityを使う。
- Reader選択でもMonitoring Contributorを含む説明があるため、アラートack／closeや監視設定変更まで無権限とは限らない。実効role assignmentを確認する。
- ReviewはAzureインフラの変更承認を扱う。メール・Teams等の外部操作は同じゲートではない。response plan／scheduled taskには既定Autonomousの説明があるため、各単位でReviewとtool policyを確認する。

根拠：[作成条件](https://learn.microsoft.com/en-us/azure/sre-agent/create-and-set-up)、[権限](https://learn.microsoft.com/en-us/azure/sre-agent/permissions)、[run modes](https://learn.microsoft.com/en-us/azure/sre-agent/run-modes)。

料金は固定4 AAU／agent-hourにmodel別token AAUが加算される。新規trialは最大30日・3 agentsで固定部分の免除が中心で、active利用は有料。固定課金はagentを削除するまで続く。公開価格ページでは通貨単価を確定できず、旧記事の単価を現行見積へ流用しない。[料金構造](https://learn.microsoft.com/en-us/azure/sre-agent/pricing-billing)、[trial](https://learn.microsoft.com/en-us/azure/sre-agent/evaluate)、[価格ページ](https://azure.microsoft.com/en-us/pricing/details/sre-agent/)

公開のmicrosoft/sre-agentはMITのlab／template集で、managed製品ランタイムのローカル配布ではない。合成の知識ファイルを渡せても、稼働するAzure agentが必要。今回はAzure固有の運用評価に限って候補とし、最初のローカル実験では使わない。[公式repo](https://github.com/microsoft/sre-agent)、[知識ファイル](https://learn.microsoft.com/en-us/azure/sre-agent/tutorial-upload-knowledge-document)

### AWS DevOps Agent

GAでAzure対応も追加したmanaged製品。AWS・Azure・on-premの複数情報源を調べる候補。初回は1 Agent SpaceとAWSの限定scopeだけで十分であり、Azureも同時に接続しない。[GA発表](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)

- 既定read-only。現行directed actionsは既定OFFで、有効化、elevated IAM role、operatorの実行時承認が必要。古い「read-onlyのみ」の説明だけで現行の修復機能を否定しない。
- AWS account、調査用IAM role、operatorアクセスを要する。AWS標準policyを出発点に対象を限定する。
- Azure連携にはEntraの同意または自前app／federated identity等が必要。Azure側Readerの接続を、Azureのwrite権限まで許可したものとはしない。

根拠：[directed actions](https://docs.aws.amazon.com/devopsagent/latest/userguide/working-with-devops-agent-working-with-directed-actions.html)、[AWSアクセス制限](https://docs.aws.amazon.com/devopsagent/latest/userguide/aws-devops-agent-security-limiting-agent-access-in-an-aws-account.html)、[Azure認証](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-integrations-and-knowledge-connecting-azure-index.html)。

現行料金は調査・評価・on-demand SREが0.0083 USD／agent-second、idleは課金なし。agent-secondはtask内の活動の累積時間で、単純な人間の待ち時間と同一とは限らない。新規trialは最初のoperational taskから2か月、各月最大10 Agent Spaces、調査20時間、評価15時間、chat20時間。超過後は従量課金、CloudWatch query等は別料金。これは料金体系の確認であり、利用者のtrial適格性や今回総額の確認ではない。[AWS料金](https://aws.amazon.com/devops-agent/pricing/)

サービス本体はローカル実行不可。MIT-0のsample plugin等はサービスへの連携例であり、サービス自体のOSS化ではない。合成証拠を使ってもAgent Spaceが必要。今回はmanagedの次候補として採用し、directed actions OFFで診断だけを見る。[assets](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-managing-assets.html)、[MIT-0 sample](https://github.com/aws-samples/sample-aws-devops-agent-claude-plugin)

### CloudWatch investigations

AWS既存環境の最短baseline候補。現行の単発調査は追加構成なしで始める経路があり、signed-in console sessionのread-only権限でmetrics・logs等を調べる。調査開始自体の権限は別途必要。単発は本人のみ閲覧でき、24時間後に削除されるため、必要な証拠をその前に保存する。[単発調査](https://docs.aws.amazon.com/en_en/AmazonCloudWatch/latest/monitoring/Investigations-Ephemeral.html)、[security](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Investigations-Security.html)

Systems Manager Automation runbookの提案・起動は別の修復操作として扱い、初回では起動しない。機能の追加料金はないが、telemetryやAPI等の費用は別。ローカル合成ファイルだけで完結する同製品の評価経路は確認できなかった。[機能](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Investigations.html)、[費用](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/investigations-costs.html)

AWSの単発診断には採用候補。マルチクラウド調査や修復エージェントの代替とまではしない。

### K8sGPTとCloudWatch Omniを初回から外す理由

K8sGPTはApache-2.0で、Kubernetesをread-onlyで調べ、LLMで説明する。kubeconfigが必要で、任意のログファイルを渡す標準analyze経路は確認できない。今回のクラスタなし条件に合わない。AWS／Azure／GCPのKubernetesを扱えることと、一般のcloudサービス横断調査は別である。[README](https://github.com/k8sgpt-ai/k8sgpt/blob/main/README.md)、[security](https://github.com/k8sgpt-ai/k8sgpt/blob/main/SECURITY_SELF_ASSESSMENT.md)、[CLI](https://github.com/k8sgpt-ai/k8sgpt/blob/v0.4.40/cmd/analyze/analyze.go)

2026年9月22日GA発表のCloudWatch Omniも関連するが、主眼はAI agentのtelemetry・品質・observability。RCAでAWS DevOps Agentと連携するため独立競合として重複計上しない。無料のローカルIDE機能が、VM障害対応をオフライン実証できることを意味しない。[GA発表](https://aws.amazon.com/blogs/aws/introducing-amazon-cloudwatch-omni-ai-powered-observability-for-generative-ai-and-agentic-workloads/)、[Omni agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-ask-the-omni-agent.html)

### Gemini Cloud AssistをGCP候補に残す条件

商用サービスで、ローカル配布のSRE runtimeではない。2026年10月7日更新docsはPreviewと明記。既存investigationsは4月10日以降、Premium Support契約またはaccount team経由のアクセス取得が必要とされる。proactive alert investigation／cost optimizationはprivate previewかつPremium Support対象。旧紹介記事だけで一般利用可能と判断しない。

通常investigationは利用者のOAuth資格と対象読取り権限を使い、そのtokenをデータ変更には使わないと明記。一方、一般chatの変更は本人の明示同意、background agentは専用service accountという別経路である。利用者のIAMが広ければ調査範囲も広がる。対象project／applicationを限定し、必要な監査log種別の有効化を確認する。

価格表にはPreview中のEnterprise対象機能の追加料金なしとの記載があるが、利用資格・Support契約・周辺サービス料金は別。対象環境の契約、割当、ログ料金は未確認なので総額未定。ローカル無料の第一候補にはしない。外部問い合わせや契約追加は今回行っていない。

[提供条件と範囲](https://docs.cloud.google.com/cloud-assist/investigations)、[作成権限](https://docs.cloud.google.com/cloud-assist/create-investigation)、[identityと承認](https://docs.cloud.google.com/cloud-assist/proactive-agents-concepts)、[料金](https://cloud.google.com/products/gemini/pricing)、[提供条件変更](https://docs.cloud.google.com/cloud-assist/deprecations/features)。

## 4 研究と benchmark から借りるもの

### ITBench

ICML 2025の研究で、SRE、CISO、FinOpsのタスクを対象にする。コードはApache-2.0。SREのself-hosted試験はKubernetes、Helm、kubectl、Ansible等とアプリ・observability・障害注入が必要。初回から構築すると、製品評価より試験基盤作りが主作業になる。

借りるのは「根本原因だけでなく、解決を別に検証する」という枠組み。live repairを評価する必要が出た後に選択する。hosted leaderboardもrepo登録・GitHub App権限等が必要で、無条件の無料即実行とは扱わない。

[論文](https://arxiv.org/abs/2502.05352)、[公式repo](https://github.com/itbench-hub/ITBench)、[実行要件](https://github.com/itbench-hub/ITBench/blob/main/documentation/getting-started/scenarios.md)、[hosted手順](https://github.com/itbench-hub/ITBench/blob/main/documentation/getting-started/leaderboard.md)

### ITBench-AA

2026年5月27日公開。incident snapshotを読み、原因entityと根拠を構造化出力する方式で、修復は測らない。公開40件と非公開19件、3回ずつの評価。原因を見逃さずに挙げた場合のprecisionを重視し、下流症状を原因に混ぜることも抑える。

公開データはCC-BY-4.0。クラスタ不要という点は今回に合うが、データ全体は約31.1GB、確認したScenario-1だけでも約1.18GB。初回の数ファイル試験には重い。次段階で少数snapshotを選び、ground_truth.yamlや答え入りdata.jsonlをagent入力から隔離して使う。

公式のharness・100-turn・judgeと、今回の1〜2runの採点は異なる。今回の結果を公式leaderboardのスコアや順位へ直接比較しない。

[評価方式](https://artificialanalysis.ai/evaluations/itbench-aa)、[方法論](https://artificialanalysis.ai/methodology/intelligence-benchmarking#itbench-aa)、[公開dataset](https://huggingface.co/datasets/ArtificialAnalysis/ITBench-AA)

### AIOpsLab

Microsoft Research系のMLSys 2025研究。MIT公開。検出、局所化、分析、緩和を、実アプリ・負荷生成・障害注入・telemetry込みで評価する。Python 3.11以上、Helm、Kubernetes等が必要で、Kind経路でもDocker等を用意する。

「提案した対応で本当に復旧したか」を後段で確認する候補。ローカル合成ログの初回では導入しない。[研究紹介](https://microsoft.github.io/AIOpsLab/)、[論文](https://arxiv.org/abs/2501.06706)、[公式repo](https://github.com/microsoft/AIOpsLab)、[Kind要件](https://github.com/microsoft/AIOpsLab/blob/main/kind/README.md)

### 学術サーベイとの統合

[学術サーベイ](survey-academic.ja.md)は中核15本、補助2本を扱う。本書では採用判断に直結する点だけを整理する。

| 段階 | 候補と発表 | 得られるもの／限界 |
| --- | --- | --- |
| 最初の同一証拠比較 | Cloud-OpsBench、2026-02初版／08-22 v2、プレプリント | 診断toolのsnapshot再生。正解と証拠充足を別採点。実修復は測らない |
| 大量データの分析 | OpenRCA、ICLR 2025 | logs・metrics・tracesの分析。容量・RAM・時刻系を確認。修復評価ではない |
| 生きた環境 | AIOpsLab、MLSys 2025／ITBench、ICML 2025 | 診断と実際の回復を分けて評価。構築・運用負担がある |
| ノイズ・複合障害 | SREGym、2026-05初版／07-30 v3、プレプリント | 後段の高難度評価。全問題にLinuxノードのSSH/rootが必要で、EKS／AKS／GKEへそのまま適用しない |
| 既製研究agent | STRATUS、NeurIPS 2025 | 診断・軽減・Undoの状態機械。単一writer、正確なUndo等の前提があり、途中悪化や不可逆APIを一般に防げない |
| 安全性 | AIOpsDoom、USENIX Security 2026 | telemetryに紛れた指示が誤対応を誘導。観測データを承認として扱わず、権限判定をモデル外に置く |
| 役割分担の比較 | mABC、Findings of EMNLP 2024／LATS-RCA、SEAA 2026／RCLAgent、2026プレプリント | 投票、仮説探索、依存関係別の分担という選択肢。多人数化をそのまま品質向上としない |

一次資料：[Cloud-OpsBench](https://arxiv.org/html/2603.00468v2)、[OpenRCA](https://microsoft.github.io/OpenRCA/)、[SREGym](https://arxiv.org/html/2605.07161v3)、[STRATUS](https://arxiv.org/html/2506.02009v2)、[AIOpsDoom](https://www.usenix.org/conference/usenixsecurity26/presentation/pasquini)、[mABC](https://aclanthology.org/2024.findings-emnlp.232/)、[LATS-RCA](https://arxiv.org/abs/2605.03505)、[RCLAgent](https://arxiv.org/abs/2605.14866)。

特にCloud-OpsBenchはMITの公開実装で、2026-10-06のcommit `ea05dafbc87b5985df8721622d63d4229c2b4224` にMCPが追加された。サーバー自体にLLM key／実クラスタは不要。Codex／OpenCode接続例があり、既存AIを作り直さず試す入口になる。ただしclientの推論費は別、Windowsネイティブ動作は未確認、MCP自体はclientのfilesystemを隔離しない。現在のJSONL traceは、そのまま付属agent用の評価形式にはならない。[MCP仕様](https://github.com/LLM4Ops/Cloud-OpsBench/blob/ea05dafbc87b5985df8721622d63d4229c2b4224/cloudopsbench_mcp/README.md)、[license](https://github.com/LLM4Ops/Cloud-OpsBench/blob/ea05dafbc87b5985df8721622d63d4229c2b4224/LICENSE)。

## 5 技術者の登壇・開発経験・実装事例

製品仕様、開発者の自己報告、デモ、査読研究を混同しない。以下の設計への反映は今回の判断であり、提供元がこのマルチクラウド構成を保証しているという意味ではない。

### Microsoft：SRE Agentのアンチパターンを扱う登壇

**真壁 徹さん「使いこなすために知っておきたい Azure SRE Agent アンチパターン」**。本人公開スライドの公開日は2026-10-07、表紙の肩書は日本マイクロソフトのシニアクラウドソリューションアーキテクト。公開transcriptの確認できた箇所を用い、全スライドの画像確認済みとはしない。

| 確認できた注意点 | 今回の回避策 |
| --- | --- |
| 全alertをAIへ流すことによる費用浪費 | SLO・severity・重複抑止で対象を絞り、既知の定型処理を先に使う |
| AIの答えを理解せず受け入れること | 証拠ID、反証、未確認点をレビューし、自己評価だけで合格にしない |
| 判断につながらないレポート | 読み手・判断・次の行動を指定し、1 incidentごとに短い採否を残す |
| 必要なcode／telemetryなしで解決を期待すること | 接続・観測欠損の台帳を作り、情報不足を能力不足や正常と誤判定しない |

資料は障害対応だけでなく、成功基準・理解・改善・運用・学びの展開まで扱う。今回も導入数や自律性の高さを目標にせず、運用判断に役立つかを測る。[本人の登壇資料](https://speakerdeck.com/torumakabe/tsukaikonasu-tame-ni-shi-te-okitai-azure-sre-agent-anchipatan)

### Microsoft：細分化したmulti-agentから少数generalistへ

**Sanchit Mehtaら、2025-12-26、Azure SRE Agent開発経験。** 多数のAzureサービス別agentの引継ぎで、発見不能、文脈汚染、反復、視野の狭まりが生じ、少数generalistと必要時に読む知識へ整理したと報告。これは特定製品の経験であり「全multi-agentが悪い」という実証ではない。広いtoolを使う記述も、広いIAMを与える根拠にはしない。

採用するのは、最初は単体baseline、追加AIは独立診断または根拠照合という限定役割、引継ぎ回数と費用を記録する方針。サービス別の多数agentを先に設計しない。[開発者記事](https://techcommunity.microsoft.com/blog/appsonazureblog/context-engineering-lessons-from-building-azure-sre-agent/4481200)

**Dalibor Kovacevic、2026-03-10、GA onboardingの実装例。** 実sample appのcode・logs・deployment・knowledgeを接続し、RBAC不足とtelemetry exporterの欠落を切り分けた。単にagent resourceを作ったことを準備完了にしない、という設計参考。内部運用から得た知見とsample appの実験であり、独立した製品比較ではない。[工程記事](https://techcommunity.microsoft.com/blog/appsonazureblog/what-it-takes-to-give-sre-agent-a-useful-starting-point/4500343)

### AWS：今回に近いAWS＋Azureの顧客実装

**James Ickes（Mary Kay Technical Architect）／Emmanuel Isimah（AWS Senior Solutions Architect）、2026-08-25。** AWS DevOps Agentの調査結果をJSONとして受け渡し、イベント・queue・workflowを介してtriage／専門agentへ分岐。SonnetとHaikuの役割分担、AgentCoreの隔離環境、Azure DevOpsのPR作成を説明する顧客共著の実運用例。

採用するのは「調査と変更を成果物で分離」「重複を抑える」「修正案をPRへ」という境界。数値は顧客自己報告で、IAM最小権限、人承認、merge、rollbackの詳細は記事だけでは不明。大規模なAWS event基盤を初回へコピーしない。[公式顧客実装](https://aws.amazon.com/blogs/industries/how-mary-kay-built-self-triaging-operations-with-amazon-bedrock-2/)

**Amit Arora／Dheeraj Oruganty、2025-09-26。** LangGraph supervisorとKubernetes・logs・metrics・runbookの4agent、AgentCoreのidentity／runtime／gatewayを用いた公開デモ。本文が合成データとstub backendと明記するため本番修復の実績には数えない。サンプルの広い権限設定を本番の最小権限として流用しない。[技術記事](https://aws.amazon.com/blogs/machine-learning/build-multi-agent-site-reliability-engineering-assistants-with-amazon-bedrock-agentcore/)、[公開実装](https://github.com/awslabs/agentcore-samples/tree/main/02-use-cases/01-conversational-agents/SRE-agent)

### Google：診断の自由度と変更の統制を分ける

**Riccardo Carlesso／Ramón Medrano Llamas、2026-01-22。** Google SREによるGemini CLI／ProdAgentの工程記事。掲載incidentはsimulation。型付きMCP操作、危険度、状況依存policy、CLIでの人承認、提案・承認の監査を説明。内部ProdAgentそのものは公開製品として再利用できない。

今回には、runbookへ検証・復旧条件を含めること、診断結果から直接APIを叩かず限定実行へ渡すことを採用する。シミュレーションと社内利用の説明を、一般利用者向けの自律修復保証としない。[Google工程記事](https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages/)

### Datadog：最終回答だけでなく調査過程を評価する

**Daniel Shan／Tristan Ratchford、2026-01-12。** 仮説を立て、telemetryで反証し、深掘りするBits AI SREの開発説明。雑多なデータの一括要約が原因推定を誤らせた例を示す。[開発記事](https://www.datadoghq.com/blog/building-bits-ai-sre/)

**Benjamin Barton、2026-04-07。** 実incidentの観測状態を保存したオフライン再生と、原因・調査過程・回帰検知を扱う。モデルやtool単体のテストだけで全体品質を保証できない点が重要。非公開の社内評価・顧客データを用いた自己報告であり、公開benchmarkとの直接比較はできない。今回にはsnapshot固定と、原因正解／証拠到達／誤操作を別採点する方針を採る。[評価基盤の記事](https://www.datadoghq.com/blog/engineering/bits-ai-eval-platform/)

### マルチAIの接続・観測の参考

- **PayPal、2026-10-08、公式実装記事。** 複数AI clientを共通MCP Hubへ接続し、tool discovery時の権限とinvoke時の再認可、下流credentialsの分離を説明。SRE agent製品そのものではない。今回には「同じtoolに見えても、実行ごとに本人・agent・対象scopeを確認する」原則だけを採用する。[MCP Hub](https://developer.paypal.com/community/blog/One_connection_2000_tools/)
- **Vipul Rajendra Gargav／Rajesh Kumar Ravi、2026-08-13、AWS公式実装例。** GCP Cloud ShellのagentをOpenTelemetry経由でAgentCore Observabilityへ接続。model呼出し、token、latency、sessionを追跡する。クラウド横断の修復や複数AI協働の実証ではない。観測先を実行cloudから切り離せる参考とし、初回はローカルtraceで足りる。[観測実装](https://aws.amazon.com/blogs/machine-learning/monitor-on-premises-and-multi-cloud-ai-agents-with-agentcore-observability/)

### 関連登壇の読み分け

| 登壇 | 日付と確認範囲 | 用途と留保 |
| --- | --- | --- |
| Arik Alon、HolmesGPT、KubeCon Europe 2026 | 会期2026-03-23〜26、作者スライドを確認 | 原因commit・PR・rollbackの段階を読む。demoの成功を本番保証にしない |
| David Yanacek／Bill Fine、AWS re:Invent 2025 COP362 | 公式動画公開2025-12-05。録画demoを含むとの登壇者説明 | 内部multi-agentと利用者側の実行権限を区別。2026-05-27技術記事で並列仮説・反証を補足 |
| Afrina M／Mir Islam／Cedric Yao、Google Cloud Next ’26 BRK2-013 | 公式動画公開2026-07-07、説明欄まで確認、字幕未確認 | PayPalのobservability・multi-agent・governanceを扱う。具体IAMや承認設定を確認済みとしない |

[HolmesGPTスライド](https://hosted-files.sched.co/kccnceu2026/9f/holmesgpt%20auto%20remediation.pdf)、[AWS公式動画](https://www.youtube.com/watch?v=JajBEYle67I)、[AWS技術記事](https://aws.amazon.com/blogs/devops/how-aws-devops-agent-uses-multi-agent-reasoning-to-find-root-causes/)、[Google公式動画](https://www.youtube.com/watch?v=8tB01DYGMAs)。

## 6 サーベイから選ぶ構成

1. **共通証拠＋単体診断**：Cloud-OpsBenchの既存MCPで1snapshotを既存AIへ渡す。新規cloudなし。HolmesGPT file-onlyは代替。
2. **比較してから協働**：別AIを同じ証拠・総予算で独立評価。その後に限り調査＋根拠照合を試す。多数決を正解や承認の代用にしない。
3. **cloud-nativeは必要時に追加**：AWS DevOps／Azure SREを権限・費用・対象で選ぶ。GCPは利用資格が不明なので導入前提にしない。
4. **変更は別経路**：人の承認、対象限定の実行、独立した復旧観測、cleanupを診断agentから分ける。既存workflowで実現できれば新規基盤を作らない。

この構成は文献と実装事例からの提案。採用を確定する実測はまだない。単体より複数AIの方が良いか、managed製品が必要かは次の小さな試験で判断する。

## 7 未確認事項

実際の採用と段階別の試験は[構成・検証計画](architecture-and-validation-plan.ja.md)を参照。

- 利用可能なローカルmodel、端末性能、必要な隔離設定、既存インストール
- 対象環境の各サービス契約、trial適格性、region、SKU、課金通貨、費用上限
- Azureの現行通貨単価、Robusta Platformの具体的無料枠と見積
- 各候補の実環境での接続、診断品質、誤操作防止、復旧、cleanup

これらは推測で埋めない。製品の存在や公式経路の確認と、対象環境で利用できること、実測で成功したことを区別する。
