"use strict";
const main=document.querySelector("#main");
const QUALITY_TOOLTIP="예측 정확도가 아니라 분석에 필요한 자료의 충실도와 적용 가능 범위를 나타냅니다.";
const DONOR_EXPLANATION="미국 연구에서 반복된 feature 방향성과 선택한 과거 기준일의 한국시장 상대 신호가 같은 방향을 지지하는 정도입니다.";
const PUBLIC_CONTEXT_EXPLANATION="현재 historical replay에서는 검증된 공개정보 시점 자료가 연결되지 않아 중립 기준값을 사용합니다. 이 값은 이상거래 근거를 의미하지 않습니다.";
const esc=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt=value=>typeof value==="number"&&Number.isFinite(value)?value.toFixed(1):"—";
const num=value=>Number(value).toLocaleString("ko-KR");
const get=async path=>{
  const response=await fetch(path,{signal:AbortSignal.timeout(25000)});
  const body=await response.json();
  if(!response.ok){const e=new Error(body.detail?.reason||body.detail||"HTTP "+response.status);e.detail=body.detail;e.status=response.status;throw e;}
  return body;
};
const title=(eyebrow,heading,lead)=>'<div class="page-title"><p class="eyebrow">'+eyebrow+'</p><h1>'+heading+'</h1><p class="lead">'+lead+'</p></div>';
const list=rows=>'<ul class="method-list">'+rows.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ul>';
const tone=level=>({LOW:"low",WATCH:"watch",REVIEW:"review",REVIEW_HIGH:"high",ABSTAIN:"abstain"}[level]||"abstain");
const riskBadge=row=>'<span class="risk-badge '+tone(row.risk_level)+'">'+esc(row.risk_label)+'</span>';
function journey(){return '<div class="journey">'+[
  ["US donor 연구","방향·표현 prior"],["한미 전이 감사","191개 산식 검토"],["KR feature adapter","24개 특징별 변환"],
  ["KR 이상도 모델","Isolation Forest"],["검토 맥락","활성화·donor / 공개정보 중립"],["설명형 검토지수","동결 정책 · 과거 재현"]
].map((x,i)=>'<div><span>0'+(i+1)+'</span><strong>'+x[0]+'</strong><p>'+x[1]+'</p></div>').join("")+'</div>';}
function meter(value,label){
  return typeof value==="number"&&Number.isFinite(value)?
    '<meter min="0" max="100" value="'+value+'" aria-label="'+esc(label)+'">'+fmt(value)+'</meter>':
    '<span class="not-observed">산출 보류</span>';
}
async function home(){
  const [demo,info]=await Promise.all([get("/api/kr/demo"),get("/api/kr/model-info")]);
  const row=demo.rows[0];
  main.innerHTML='<section class="hero"><div><p class="eyebrow">KOREA FIRST · HISTORICAL RESEARCH</p><h1>한국시장 이상 움직임을<br><span>시장·자기과거·동종종목·미국 연구패턴과 비교해</span><br>우선 검토할 종목과 이유를 보여줍니다.</h1><p class="lead">KR FrontWatch AI는 선행매매와 같은 사전 이상거래의 조기 검토를 지원하기 위해 만든 시장감시 연구용 AI입니다.</p><div class="badges hero-scope"><span class="badge neutral">HISTORICAL REPLAY · 2023 과거 자료</span><span class="badge neutral">실시간 아님</span><span class="badge neutral">법적 판단·투자 추천 아님</span></div><p class="hero-copy muted">한국 비라벨 자료에 별도로 학습한 이상도 모델이 핵심입니다. 미국 연구의 방향성과 단기 활성화가 해석을 보완합니다.</p><div class="actions"><a class="button" href="/kr">한국 종목 분석 →</a><a class="button secondary" href="/us">미국 Donor Research</a></div><div class="status-line"><span class="badge">한국 모델 연결 완료</span><span class="badge neutral">'+esc(demo.latest_broad_date)+' 기준 과거 재현</span></div><p class="legal-note">실시간 분석이 아닙니다. 시점 검증 공개정보는 미연결이며 범죄 확률을 산출하지 않습니다.</p></div><aside class="panel hero-panel"><p class="eyebrow">FIXED COHORT · ACTUAL CACHED RESULT</p><h2>'+esc(row.name)+' <small>'+esc(row.security_code)+'</small></h2><p class="muted">'+esc(row.analysis_date)+' · '+esc(row.exchange)+' · 동결 데모 첫 번째 사례</p><div class="home-score"><div><span>이상 사전거래 검토지수</span><strong>'+fmt(row.risk_index)+'</strong></div>'+riskBadge(row)+'</div><div class="score-meter">'+meter(row.risk_index,"검토지수")+'</div><div class="metric-row"><div><strong>'+fmt(row.confidence_index)+'</strong><span title="'+esc(QUALITY_TOOLTIP)+'">데이터 품질·가용성 / 100 ⓘ</span></div><div><strong>'+info.model.input_features+'</strong><span>KR 핵심 특징</span></div><div><strong>'+num(info.latest_cache_rows)+'</strong><span>최신 기준일 캐시 행</span></div></div><p class="legal-note spaced">자료 범위 제한 있음 · LIMITED<br>법적 위법 확률이 아니라 추가 검토 우선순위를 위한 상대 지수입니다.</p><a href="/kr">실제 분석 결과와 근거 보기 →</a></aside></section><section><h2>미국 연구를 한국의 정답으로 옮기지 않습니다.</h2>'+journey()+'<div class="three-grid"><article class="panel value-card"><span class="num">01 / KOREAN TARGET</span><h3>한국 종목 분석</h3><p>지원 날짜의 정확한 코드·이름을 검색하고, 동결된 검토지수·데이터 품질·가용성·관측 근거를 확인합니다.</p><p class="spaced"><a href="/kr">한국 분석 →</a></p></article><article class="panel value-card"><span class="num">02 / US DONOR</span><h3>미국 연구패턴 지원</h3><p>미국 계수·확률을 이식하지 않습니다. 특징 방향성과 표현의 연구 근거를 별도로 확인합니다.</p><p class="spaced"><a href="/us">미국 연구 →</a></p></article><article class="panel value-card"><span class="num">03 / CROSS-MARKET</span><h3>191개 감사에서 core24로</h3><p>전체 전이 진단과 실제 한국 모델에 선택된 특징의 수를 구분해 보여줍니다.</p><p class="spaced"><a href="/transfer">US↔KR Transfer Audit →</a></p></article></div></section>';
}
function renderResult(row,info){
  const container=document.querySelector("#kr-result");
  const components=[
    ["한국시장 이상도","kr_market_anomaly","KR_ANOMALY",info.explanation.kr_market_anomaly],
    ["단기 활성화","activation_index","ACTIVATION",info.explanation.activation_index],
    ["미국 연구패턴 지원도","us_donor_support_effective","DONOR_EFFECTIVE",DONOR_EXPLANATION],
    ["공개정보 맥락 · 중립","public_context_term","PUBLIC_CONTEXT",info.explanation.public_context]
  ];
  const nullRisk=row.risk_index===null;
  container.innerHTML='<div class="two-grid"><section class="panel result-summary" data-risk-level="'+esc(row.risk_level)+'"><div class="result-heading"><div><p class="eyebrow">'+esc(row.exchange)+' · '+esc(row.analysis_date)+'</p><h2>'+esc(row.name)+' <small>'+esc(row.security_code)+'</small></h2></div>'+riskBadge(row)+'</div><p class="score-caption">이상 사전거래 검토지수 <abbr title="법적 위법 확률이 아니라 추가 검토 우선순위를 위한 상대 지수입니다.">ⓘ</abbr></p><div class="big-score" id="risk-value">'+(nullRisk?"산출 보류":fmt(row.risk_index)+' <small>/ 100</small>')+'</div><div class="score-meter">'+meter(row.risk_index,"이상 사전거래 검토지수")+'</div><div class="confidence-line"><strong title="'+esc(QUALITY_TOOLTIP)+'">데이터 품질·가용성 ⓘ '+fmt(row.confidence_index)+' / 100</strong><span class="badge neutral">'+esc(row.domain_gate)+'</span></div><p class="legal-note">'+(nullRisk?"사용 조건 미충족으로 점수를 보류했습니다. 0점이나 정상 판정이 아닙니다.":"자료 범위 제한 있음 · 통계적 신뢰구간이나 위법 확률이 아닙니다.")+'</p><p class="technical-note">동결 과거 분석 · 라이브 추론 없음 · ALERT 생성 없음</p></section><section class="panel"><h2>검토지수의 구성</h2><p class="muted">한국시장 이상도가 핵심이며 다른 요소가 검토 맥락을 보완합니다.</p><div class="component-chart">'+components.map(([label,key,weight,explain])=>key==="public_context_term"?'<div class="component-row context-neutral" data-state="unavailable"><strong>공개정보 맥락</strong><span>자료 시점 미연결</span><p>중립 기준값 '+fmt(row[key])+'</p><small>'+esc(PUBLIC_CONTEXT_EXPLANATION)+'</small><small>고정 정책의 중립 입력 · 가중치 '+(info.score_policy.weights[weight]*100)+'% 유지</small></div>':'<div class="component-row"><div><span title="'+esc(explain)+'">'+label+' ⓘ</span><strong>'+fmt(row[key])+'</strong></div>'+meter(row[key],label)+'<small>고정 가중치 '+(info.score_policy.weights[weight]*100)+'% · 기여 '+(typeof row[key]==="number"?fmt(row[key]*info.score_policy.weights[weight]):"—")+'점</small></div>').join("")+'</div><p class="legal-note donor-explanation">'+esc(DONOR_EXPLANATION)+'</p><p class="legal-note">동결 휴리스틱 조합입니다. 동일한 비중의 AI 모델 4개가 아닙니다.</p></section></div><section class="panel spaced"><h2>왜 이런 결과인가요?</h2>'+list(row.plain_language_explanations||[])+'<div class="feature-reasons">'+(row.top_feature_explanations||[]).map(f=>'<article><strong>'+esc(f.display_name||f.feature)+' <span class="badge neutral">Tier '+esc(f.tier)+'</span></strong><p>'+esc(f.text)+'</p></article>').join("")+'</div>'+(row.top_feature_explanations?.length?"":'<p class="muted">이 행은 사용할 수 있는 특징 근거가 부족해 설명을 보류합니다.</p>')+'</section><section class="three-grid spaced">'+[
    ["자기이력 특징 극단성","self_history_anomaly",info.explanation.self_history_anomaly],
    ["시장 상대 특징 극단성","market_relative_anomaly",info.explanation.market_relative_anomaly],
    ["동종종목 특징 극단성","peer_relative_anomaly",info.explanation.peer_relative_anomaly]
  ].map(([label,key,explain])=>'<article class="panel"><h3>'+label+'</h3><div class="big-score small-score">'+fmt(row[key])+'</div><p class="legal-note">'+esc(explain)+'</p></article>').join("")+'</section><section class="panel spaced public-context-card" data-state="unavailable"><h2>공개정보 맥락</h2><p><strong>자료 시점 미연결</strong> · 중립 기준값 '+fmt(row.public_context_term)+'</p><p>'+esc(PUBLIC_CONTEXT_EXPLANATION)+'</p><div class="badges"><span class="badge neutral">'+esc(row.evidence_route)+'</span><span class="badge neutral">'+esc(row.timing_state)+'</span></div><p class="legal-note spaced">중립 기준값을 적용하며 ALERT는 생성하지 않습니다. 공개정보가 없다는 사실을 위법 근거로 해석하지 않습니다. 공시 타임라인이나 공시 전후 판정은 제공하지 않습니다.</p></section><details><summary>모델·자료 상태와 한계</summary><dl><div><dt>모델</dt><dd>KR Isolation Forest · 24개 특징</dd></div><div><dt>자료 기준일</dt><dd>'+esc(row.data_as_of)+'</dd></div><div><dt>판단 기준</dt><dd>'+esc(row.decision_as_of)+'</dd></div><div><dt>관측 이력 / 동종군</dt><dd>'+esc(row.history_sessions??"—")+' / '+esc(row.peer_sample_size??"—")+'</dd></div><div><dt>모델 SHA256</dt><dd class="mono">'+esc(info.model.model_SHA)+'</dd></div></dl>'+list(row.limitations||[])+'<p>공식 기업행위·재상장·거래정지 master와 시점 검증 공개정보가 없습니다. 2021 자료 공백이 있으며 2026년 연구 prior를 사용한 과거 재현으로 당시의 사전 검증이 아닙니다.</p><a href="/methodology">전체 방법론 확인 →</a></details>';
}

function savedReviews(){
  try{return JSON.parse(localStorage.getItem("frontwatch_reviews_v1")||"[]").filter(x=>/^[0-9]{6}$/.test(x.code)&&/^[0-9-]{10}$/.test(x.date)).slice(0,30);}
  catch(_){return [];}
}
function storeReviews(rows){
  try{localStorage.setItem("frontwatch_reviews_v1",JSON.stringify(rows.slice(0,30)));return true;}catch(_){return false;}
}
function reviewActions(row){
  const mount=document.querySelector("#kr-result");
  const block=document.createElement("section");
  block.className="panel spaced workflow-panel";
  block.innerHTML='<p class="eyebrow">ANALYST WORKFLOW · HUMAN REVIEW</p><h2>선행매매 관점에서, 다음에 확인할 것은?</h2><div class="review-path"><article><span>01 · 시장 신호</span><strong>'+(row.risk_index===null?"자료 조건 미충족":"기준일 이례성과 특징 확인")+'</strong><p>한국시장 이상도·자기이력·동종군과 관측 근거를 함께 검토합니다.</p></article><article><span>02 · 정보와 시점</span><strong>공개정보 대조 대기</strong><p>당시 공개된 정보와 시장 움직임의 정확한 시점을 확인해야 합니다. 현재 자료는 미연결입니다.</p></article><article><span>03 · 추가 검토</span><strong>선행매매 여부 판단 불가</strong><p>기업행위·거래정지 등 다른 설명과 공식 증거를 분석가가 확인해야 합니다.</p></article></div><div class="actions"><button type="button" class="primary" id="save-review">검토목록에 저장</button><button type="button" class="secondary" id="copy-review">결과 요약 복사</button><button type="button" class="secondary" id="export-reviews">검토목록 CSV</button></div><p id="action-status" class="form-status" role="status" aria-live="polite">검토목록은 이 브라우저에만 저장됩니다. 서버 전송·범죄 판정 기능이 아닙니다.</p><details><summary>내 검토목록 <span id="saved-count"></span></summary><div id="saved-items"></div></details><details><summary>처음 보는 분을 위한 지표 안내</summary><p><strong>검토지수:</strong> 추가 검토의 상대 우선순위이며 범죄 확률이 아닙니다.</p><p><strong>데이터 품질·가용성:</strong> 예측 정확도가 아니라 분석에 필요한 자료의 충실도와 적용 가능 범위를 나타냅니다. 위험도·통계적 신뢰구간과 다릅니다.</p><p><strong>정상 범위:</strong> 동결 정책에서 낮은 상대지수 구간이라는 뜻입니다. 위법행위 부재나 투자 안전을 증명하지 않습니다.</p><p><strong>공개정보 미연결:</strong> 관련 정보가 없었다는 뜻이 아닙니다. 이 데모에 시점 검증 자료가 연결되지 않은 상태입니다.</p></details>';
  mount.append(block);
  const message=block.querySelector("#action-status");
  function renderSaved(){
    const rows=savedReviews();block.querySelector("#saved-count").textContent="("+rows.length+"/30)";
    const target=block.querySelector("#saved-items");
    target.innerHTML=rows.length?rows.map((x,i)=>'<div class="saved-row"><div><strong>'+esc(x.name)+'</strong><small>'+esc(x.code)+' · '+esc(x.date)+' · 과거 재현</small></div><button type="button" class="secondary" data-open="'+i+'">다시 보기</button><button type="button" class="secondary" data-remove="'+i+'">삭제</button></div>').join(""):'<p class="muted spaced">저장한 검토 대상이 없습니다.</p>';
    for(const button of target.querySelectorAll("[data-open]"))button.addEventListener("click",()=>{
      const chosen=rows[Number(button.dataset.open)];
      document.querySelector("#code").value=chosen.code;
      document.querySelector("#as-of").value=chosen.date;
      document.querySelector("#kr-form").dispatchEvent(new Event("submit",{bubbles:true,cancelable:true}));
      document.querySelector("#kr-form").scrollIntoView({block:"start",behavior:"smooth"});
    });
    for(const button of target.querySelectorAll("[data-remove]"))button.addEventListener("click",()=>{
      if(storeReviews(rows.filter((_,i)=>i!==Number(button.dataset.remove)))){renderSaved();message.textContent="이 브라우저의 검토목록에서 삭제했습니다.";}
      else message.textContent="브라우저 저장소를 사용할 수 없습니다.";
    });
  }
  renderSaved();
  block.querySelector("#save-review").addEventListener("click",()=>{
    const rows=savedReviews().filter(x=>!(x.code===row.security_code&&x.date===row.analysis_date));
    rows.unshift({code:row.security_code,date:row.analysis_date,name:row.name});
    message.textContent=storeReviews(rows)?"기준일과 종목을 이 브라우저 검토목록에 저장했습니다. 모델 결과나 정책은 바뀌지 않습니다.":"브라우저 저장소를 사용할 수 없습니다.";
    renderSaved();
  });
  block.querySelector("#copy-review").addEventListener("click",async()=>{
    const summary=["KR FrontWatch AI · 과거시장 연구 재현",row.name+" ("+row.security_code+") / "+row.exchange,
      "자료 기준일: "+row.analysis_date+" (실시간 아님)",
      "검토지수: "+fmt(row.risk_index)+" / 100 · "+row.risk_label,
      "데이터 품질·가용성: "+fmt(row.confidence_index)+" / 100 · "+row.domain_gate,
      "공개정보 시점 자료: 미연결 / 중립 50 / ALERT 없음",
      "선행매매 여부를 판정하지 않습니다. 법적 위법 확률이나 투자 추천이 아닙니다.",
      ...(row.top_feature_explanations||[]).map(x=>x.text)].join("\n");
    try{await navigator.clipboard.writeText(summary);message.textContent="기준일·결과·한계를 포함한 요약을 복사했습니다.";}
    catch(_){message.textContent="자동 복사가 허용되지 않았습니다. 아래 요약을 직접 선택해 복사하세요.";const box=document.createElement("textarea");box.className="copy-fallback";box.readOnly=true;box.value=summary;block.append(box);box.focus();box.select();}
  });
  block.querySelector("#export-reviews").addEventListener("click",()=>{
    const rows=savedReviews();if(!rows.length){message.textContent="먼저 검토목록에 종목을 저장해 주세요.";return;}
    const quote=v=>'"'+String(v).replace(/"/g,'""')+'"';
    const csv="\uFEFFsecurity_code,name,analysis_date,mode\r\n"+rows.map(x=>[x.code,x.name,x.date,"HISTORICAL_REPLAY_NOT_A_LEGAL_FINDING"].map(quote).join(",")).join("\r\n");
    const url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
    const anchor=document.createElement("a");anchor.href=url;anchor.download="frontwatch_historical_review_list.csv";anchor.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);message.textContent="검토목록 CSV를 내려받았습니다. 코드 열은 문자열로 가져오면 앞자리 0을 보존할 수 있습니다.";
  });
}

async function kr(){
  const [demo,info]=await Promise.all([get("/api/kr/demo"),get("/api/kr/model-info")]);
  main.innerHTML=title("KR TARGET DOMAIN · FROZEN HISTORICAL REPLAY","한국시장 기준일 분석","지원되는 과거 날짜의 동결 결과입니다. 현재 시장 위험이나 실시간 예측이 아닙니다.")+
    '<section class="panel kr-controls"><form id="kr-form"><div class="replay-controls"><label>종목명 또는 코드<input id="code" maxlength="80" list="security-options" autocomplete="off" required value="'+esc(demo.rows[0].security_code)+'"><datalist id="security-options"></datalist></label><label>지원 기준일<select id="as-of">'+[...info.supported_dates].reverse().map(d=>'<option value="'+d+'">'+d+' · '+(d===info.latest_broad_replay_date?'전체시장 과거 재현':'고정 12종목 데모')+'</option>').join("")+'</select></label><button class="primary" type="submit">기준일 분석</button></div><div class="demo-controls"><label for="demo-select">고정 12개 데모</label><select id="demo-select">'+demo.rows.map(row=>'<option value="'+row.security_code+'">'+esc(row.exchange+' · '+row.name+' ('+row.security_code+')')+'</option>').join("")+'</select><small>점수와 무관하게 동결한 순서</small></div></form><p id="date-scope" class="date-scope" role="status"></p><p id="form-status" role="status" class="form-status" aria-live="polite">동결된 첫 번째 데모를 표시합니다.</p></section><div id="kr-result" class="spaced"></div>';
  renderResult(demo.rows[0],info);reviewActions(demo.rows[0]);
  let options=[];let searchTimer;let generation=0;let analysisGeneration=0;
  const code=document.querySelector("#code"),date=document.querySelector("#as-of"),status=document.querySelector("#form-status");
  const updateScope=()=>{
    const broad=date.value===info.latest_broad_replay_date;
    const scope=document.querySelector("#date-scope");
    scope.textContent=broad?"이 기준일은 전체시장 과거 재현 캐시 "+num(info.date_row_counts[date.value])+"행을 지원합니다. 전체 상장종목 모두를 보장하지는 않습니다.":"이 기준일은 고정 데모 12종목만 지원합니다.";
    scope.classList.toggle("demo-only",!broad);
  };
  updateScope();
  const refreshOptions=async()=>{
    const id=++generation,q=code.value.trim(),day=date.value;
    try{
      const found=await get("/api/kr/securities?q="+encodeURIComponent(q)+"&date="+day+"&limit=10");
      if(id!==generation)return;
      options=found.items.slice(0,10);
      document.querySelector("#security-options").innerHTML=options.map(x=>'<option value="'+esc(x.name)+'" label="'+esc(x.security_code+' · '+x.exchange)+'"></option>').join("");
    }catch(e){if(id===generation)status.textContent=e.message;}
  };
  code.addEventListener("input",()=>{analysisGeneration++;generation++;status.textContent="종목을 변경했습니다. 기준일 분석을 눌러 결과를 확인하세요.";document.querySelector("#kr-result").innerHTML="";clearTimeout(searchTimer);searchTimer=setTimeout(refreshOptions,180);});
  date.addEventListener("change",()=>{analysisGeneration++;updateScope();status.textContent="날짜를 변경했습니다. 기준일 분석을 눌러 해당 날짜의 결과를 확인하세요.";document.querySelector("#kr-result").innerHTML="";refreshOptions();});
  const run=async()=>{
    const requestId=++analysisGeneration,requestedDate=date.value;
    updateScope();
    status.textContent="정확한 코드·기준일의 동결 결과를 확인 중입니다.";
    document.querySelector("#kr-result").innerHTML="";
    let exact=code.value.trim();
    try{
      if(!/^[0-9]{6}$/.test(exact)){
        const found=await get("/api/kr/securities?q="+encodeURIComponent(exact)+"&date="+requestedDate+"&limit=200");
        if(requestId!==analysisGeneration)return;
        const matches=found.items.filter(x=>x.name===exact);
        if(matches.length!==1)throw new Error("해당 기준일의 정확한 종목명 또는 검색 목록의 6자리 코드를 선택해 주세요.");
        exact=matches[0].security_code;code.value=exact;
      }
      const row=await get("/api/kr/analyze/"+encodeURIComponent(exact)+"?date="+requestedDate);
      if(requestId!==analysisGeneration)return;
      renderResult(row,info);reviewActions(row);
      status.textContent=row.name+" · "+row.analysis_date+" 동결 결과를 표시합니다. 실시간 분석이 아닙니다.";
    }catch(e){
      if(requestId!==analysisGeneration)return;
      status.textContent=({DATA_NOT_AVAILABLE_FOR_DATE:"지원하지 않는 날짜입니다. 지원 기준일만 선택해 주세요.",SECURITY_NOT_AVAILABLE_FOR_DATE:"해당 종목은 선택한 날짜의 캐시에 없습니다. 다른 날짜 결과로 대체하지 않습니다."}[e.message]||e.message);
    }
  };
  document.querySelector("#kr-form").addEventListener("submit",e=>{e.preventDefault();run();});
  document.querySelector("#demo-select").addEventListener("change",e=>{code.value=e.target.value;run();});
}
async function us(){
  const d=await get("/api/us/donor-demo"),s=d.research_summary;
  main.innerHTML=title("US DONOR RESEARCH · NOT KR MODEL OUTPUT","미국 연구는 참고 근거입니다.","미국의 방향·표현 prior를 활용하되 미국 점수·계수·확률·calibration을 한국 모델로 직접 옮기지 않았습니다.")+
  '<div class="stats-bar"><div class="stat"><strong>'+num(s.full_research_event_rows)+'</strong><span>movement/event 행</span></div><div class="stat"><strong>'+s.full_research_CIKs+'</strong><span>고유 CIK</span></div><div class="stat"><strong>'+s.full_route_counts.WATCH+' / '+s.full_route_counts.REVIEW+'</strong><span>전체 WATCH / REVIEW</span></div><div class="stat"><strong>'+d.row_count+'</strong><span>동결 연구 사례</span></div></div><div class="callout warning">미국 scientific qualification: '+esc(s.scientific_qualification)+' · 연구용 제한 릴리스. 범죄 판정·성공 예측 사례·한국 탐지 정확도가 아닙니다.</div><section class="panel"><h2>동결된 미국 연구 사례 '+d.row_count+'개</h2><p class="muted">DEMO31: WATCH '+s.demo_route_counts.WATCH+' / REVIEW '+s.demo_route_counts.REVIEW+' · 기존 authority 순서 보존</p><table><thead><tr><th>종목</th><th>TSTAR</th><th>연구 점수</th><th>연구 경로</th><th>공개 맥락</th></tr></thead><tbody>'+d.rows.map(row=>'<tr><td data-label="종목"><strong>'+esc(row.ticker)+'</strong><small>'+esc(row.CIK)+'</small></td><td data-label="TSTAR">'+esc(row.TSTAR.slice(0,10))+'</td><td data-label="연구 점수">'+Number(row.market_score).toFixed(4)+'</td><td data-label="연구 경로">'+esc(row.stage4_route)+'</td><td data-label="공개 맥락"><small>'+esc(row.evidence_route)+'</small></td></tr>').join("")+'</tbody></table></section><details><summary>연구 제한과 출처</summary><p>2,098은 종목 수가 아닌 movement/event 행 수입니다. 시장 점수는 보정된 범죄 확률이 아닙니다. 미국의 공개정보 상태는 한국의 공개정보 미연결 상태와 구분됩니다.</p><p>한국 학습 입력에 미국 점수·계수·calibration을 넣지 않았습니다. US 모델을 수정하거나 새로 학습하지 않았습니다.</p><p class="mono">Source SHA256: '+esc(s.source_SHA)+'</p></details>';
}
function tierChart(counts,total,label){
  return '<div class="tier-chart" aria-label="'+label+'">'+["A","B","C","D","E"].map(t=>'<div class="tier-row"><span>Tier '+t+'</span><meter min="0" max="'+total+'" value="'+(counts[t]||0)+'" aria-label="'+label+' Tier '+t+'">'+(counts[t]||0)+'</meter><strong>'+(counts[t]||0)+'</strong></div>').join("")+'</div>';
}
async function transfer(){
  const d=await get("/api/transfer/audit"),m=d.reported_handoff_metrics;
  const full=Object.fromEntries(["A","B","C","D","E"].map(t=>[t,m.Tier_counts[Object.keys(m.Tier_counts).find(k=>k.startsWith("TIER_"+t+"_"))]]));
  main.innerHTML=title("US ↔ KR · AUDIT TO RUNTIME","191개 전체 감사에서, 한국 core24로","계산 가능한 모든 미국 특징을 복사하지 않았습니다. 전체 전이 감사와 실제 한국 모델에 선택된 특징은 서로 다른 통계입니다.")+
  '<div class="stats-bar"><div class="stat"><strong>'+m.Daily_CORE_recomputable+'</strong><span>전체 공통 산식 감사</span></div><div class="stat"><strong>'+m.KR_coverage_ge90_features+'</strong><span>KR coverage ≥90% feature</span></div><div class="stat"><strong>'+m.feature_movement_sign_agreement_mean.toFixed(3)+'</strong><span>feature–movement 방향 일치 평균</span></div><div class="stat"><strong>'+m.correlation_similarity.SELF.toFixed(3)+'</strong><span>자기정규화 상관구조 유사도</span></div></div><div class="two-grid"><section class="panel"><p class="eyebrow">FULL PORTABILITY AUDIT</p><h2>전체 감사 · 191개</h2>'+tierChart(full,191,"전체 감사")+'</section><section class="panel"><p class="eyebrow">FINAL KR RUNTIME SELECTION</p><h2>실제 모델 · '+d.runtime_mapping.features+'개</h2>'+tierChart(d.runtime_mapping.tier_counts,24,"한국 core24")+'</section></div><div class="callout">Tier는 전이 방식 분류입니다. 한국 탐지 정확도·투자 안전등급이 아닙니다. 실제 모델은 A14 / B1 / C6 / D3 / E0을 사용합니다.</div><section class="panel"><h2>한국 자료에서 특징별로 변환합니다.</h2>'+list(["Tier A: 한국 median/IQR 기반 robust 변환","Tier B: 같은 거래소·기준일 시장 rank","Tier C: 이전 최대 252관측의 자기이력 ECDF","Tier D: 동종군 rank 및 조건부 감쇠","rank → self → peer를 모든 특징에 직렬 중복 적용하지 않음"])+'<p>미국 prior는 움직임 강도 관련 방향입니다. 미국 회귀계수·확률·calibration은 재사용하지 않습니다.</p></section><section class="panel spaced"><h2>원본 전이 감사의 표본</h2><dl><div><dt>Movement roots</dt><dd>US '+num(m.US_full_movement_roots)+' / KR '+num(m.KR_full_movement_roots)+'</dd></div><div><dt>비교 cohort</dt><dd>US '+num(m.US_comparable_roots)+' / KR '+num(m.KR_comparable_roots)+'</dd></div><div><dt>Raw / rank / self 상관구조</dt><dd>'+m.correlation_similarity.RAW.toFixed(3)+' / '+m.correlation_similarity.RANK.toFixed(3)+' / '+m.correlation_similarity.SELF.toFixed(3)+'</dd></div></dl><p class="legal-note spaced">roots는 불법 사건 수나 현재 지원 종목 수가 아닙니다. 한국 모델 학습·reference 행 수도 아닙니다.</p></section><details open><summary>전이 진단의 해석 한계</summary><p>전역 유사성 '+esc(d.original_decision.overall_domain_similarity)+', 사건 기제·시각 권한·movement geometry는 LOW입니다. 이 수치는 한국 위법 탐지 성능 인증이 아닙니다.</p><p>원본 prior는 2018–2023 시장 연구를 포함합니다. 현재 2023 재현 결과는 미노출 사전 검증이 아닙니다.</p></details>';
}
async function methodology(){
  const d=await get("/api/methodology"),m=d.model,p=d.score_policy,e=d.explanation;
  main.innerHTML=title("METHOD · AUTHORITY · LIMITATIONS","한국에서 별도 학습하고, 과거 결과를 재현합니다.","비지도 시장 이상도 모델과 동결된 휴리스틱 정책의 연구용 구현입니다. 위법행위 지도학습 분류기나 실시간 서비스가 아닙니다.")+journey()+
  '<div class="stats-bar"><div class="stat"><strong>'+num(m.training_rows)+'</strong><span>한국 학습 행 · 2019년까지</span></div><div class="stat"><strong>'+num(m.reference_rows)+'</strong><span>별도 2020년 reference 행</span></div><div class="stat"><strong>'+m.model_params.n_estimators+'</strong><span>Isolation Forest trees</span></div><div class="stat"><strong>'+m.input_features+'</strong><span>최종 runtime 특징</span></div></div><div class="two-grid"><section class="panel"><h2>모델과 비교 기준</h2><p>'+esc(e.kr_market_anomaly)+'</p><p>seed '+m.model_params.random_state+' · contamination auto · 한국 비라벨 자료로 별도 학습. 미국 계수·확률·calibration 재사용은 모두 false입니다.</p><p>'+esc(DONOR_EXPLANATION)+'</p><p>'+esc(e.donor_support)+'</p></section><section class="panel"><h2>동결 검토지수 정책</h2><p>0.50 × 한국 이상도 + 0.15 × 활성화 + 0.20 × 감쇠 donor 지원 + 0.15 × 공개정보 맥락</p><p>데이터 품질·가용성(confidence) &lt; '+p.confidence_min+' 또는 UNSAFE는 ABSTAIN. 그 외 35 미만 정상 범위, 55 미만 관찰 필요, 70 미만 주의, 100 이하 위험·우선검토입니다.</p><p>LIMITED의 데이터 품질·가용성 상한은 '+p.LIMITED_confidence_cap+'입니다. 데이터 품질·가용성은 예측 정확도가 아닌 자료 지수이며 통계적 신뢰구간이 아닙니다.</p></section></div><section class="panel spaced"><h2>데이터·시점의 실제 범위</h2>'+list(["원자료 기간: 2018 / 2019 / 2020 / 2022 / 2023. 2021 공백을 연결해 이력을 만들지 않습니다.","한국 최신 광범위 캐시: "+d.latest_broad_date+". 추가 2023-03-31, 06-30, 09-27은 고정 12개 데모만 지원합니다.","원자료의 2,859개 security code는 기간 전체의 코드 수이며 현재 지원 기업 수나 발행사 수가 아닙니다.","공식 기업행위·재상장·거래정지·canonical issuer master가 없고 조정되지 않은 자료의 한계가 남아 LIMITED/UNSAFE로 구분합니다.","공개정보는 EVIDENCE_UNAVAILABLE, 시점은 TIMING_AMBIGUOUS, 맥락은 중립 50입니다. 공시 전 이상 움직임을 입증하거나 ALERT를 생성하지 않습니다."])+'</section><section class="panel spaced"><h2>과거 재현과 미노출 검증은 다릅니다.</h2><p>모델 학습은 2019년까지, reference는 2020년이지만 특징·prior·정책 연구는 2026년에 이루어졌고 2018–2023 진단을 포함합니다. 따라서 2023 replay를 당시의 사전 검증이나 새 봉인검증으로 주장하지 않습니다.</p><p>이번 Desktop 통합은 새 모델 학습·임계값 변경·외부 시장 데이터 수집을 수행하지 않았습니다. 캐시를 읽으며 새 추론이나 외부 생성형 AI를 호출하지 않습니다.</p><p>미국 scientific qualification은 BLOCKED입니다. 해시 일치나 화면/API 검사는 과적합·미래누수 부재 또는 법적 정확성을 보증하지 않습니다.</p></section><details><summary>원본 한계 목록과 해시</summary>'+list(d.limitations.items)+'<p class="mono">KR model SHA256: '+esc(m.model_SHA)+'</p><p class="mono">KR adapter SHA256: '+esc(m.adapter_SHA)+'</p></details>';
}
for(const link of document.querySelectorAll("nav a"))if(link.getAttribute("href")===location.pathname)link.setAttribute("aria-current","page");
const routes={"/":home,"/kr":kr,"/us":us,"/transfer":transfer,"/methodology":methodology};
(routes[location.pathname]||home)().catch(error=>{
  main.innerHTML='<section class="panel status-error"><h1>자료를 불러오지 못했습니다.</h1><p>'+esc(error.message)+'</p><p>빈 결과를 정상이나 0점으로 표시하지 않습니다.</p><button id="retry" class="secondary">다시 시도</button></section>';
  document.querySelector("#retry").addEventListener("click",()=>location.reload());
});
