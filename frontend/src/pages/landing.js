// Landing page — Slogan, concept, and the anti-thesis of永久保存.

export function renderLanding(container) {
  container.innerHTML = `
    <section class="landing">
      <div class="hero">
        <h1 class="slogan-zh">万物终将风化，<br/>连遗忘本身也会被遗忘。</h1>
        <p class="slogan-en">"Everything decays. Even the memory of forgetting."</p>
        <div class="hero-sub">
          一座所有事物都会风化的数字墓园。为文字、代码、图片、链接立碑，<br/>
          然后看着它们随真实时间一起褪色、崩塌、消散。<br/>
          A digital graveyard where even the tombstones crumble.
        </div>
        <a href="#/graveyard" class="cta">立下第一块碑 · Erect your first stone</a>
      </div>

      <div class="concept">
        <div class="vs-card keep">
          <div class="vs-title">所有其他产品<br/><span>Every other product</span></div>
          <ul>
            <li>永久保存 · Store forever</li>
            <li>云端备份 · Cloud backup</li>
            <li>永不丢失 · Never lose a byte</li>
          </ul>
        </div>
        <div class="vs-divider">×</div>
        <div class="vs-card decay">
          <div class="vs-title">熵逝碑林<br/><span>Entropy Epitaph</span></div>
          <ul>
            <li>必然消逝 · Everything must fade</li>
            <li>无法逆转 · Entropy is one-way</li>
            <li>连证明也会消失 · Even the proof disappears</li>
          </ul>
        </div>
      </div>

      <div class="rules">
        <h2>熵增闭环 · The Entropy Loop</h2>
        <div class="rule-steps">
          <div class="rule-step">
            <div class="rs-num">1</div>
            <div class="rs-title">立碑 · Erect</div>
            <div class="rs-body">为任何死去的数字之物立一块墓碑。</div>
          </div>
          <div class="rule-arrow">→</div>
          <div class="rule-step">
            <div class="rs-num">2</div>
            <div class="rs-title">风化 · Decay</div>
            <div class="rs-body">碑文与碑体随真实时间持续瓦解，无法阻止。</div>
          </div>
          <div class="rule-arrow">→</div>
          <div class="rule-step">
            <div class="rs-num">3</div>
            <div class="rs-title">擦拭 · Delay</div>
            <div class="rs-body">每天一次擦拭，只能延缓，越到后期越无力。</div>
          </div>
          <div class="rule-arrow">→</div>
          <div class="rule-step">
            <div class="rs-num">4</div>
            <div class="rs-title">寂灭 · Vanish</div>
            <div class="rs-body">碑体崩塌，生成一张同样会消逝的凭证。</div>
          </div>
          <div class="rule-arrow">→</div>
          <div class="rule-step">
            <div class="rs-num">5</div>
            <div class="rs-title">遗忘 · Forget</div>
            <div class="rs-body">凭证继续熵增，终从档案消失，连"存在过"也被忘记。</div>
          </div>
        </div>
      </div>

      <div class="rules">
        <h2>可以埋葬什么 · What you can bury</h2>
        <div class="rule-steps">
          <div class="rule-step"><div class="rs-title">代码碑</div><div class="rs-body">废弃项目、夭折需求、不会合并的分支</div></div>
          <div class="rule-step"><div class="rs-title">遗物碑</div><div class="rs-body">没说出口的话、结束的关系、放弃的梦想</div></div>
          <div class="rule-step"><div class="rs-title">图片碑</div><div class="rs-body">删掉的照片、模糊的脸、不再存在的地方</div></div>
          <div class="rule-step"><div class="rs-title">链接碑</div><div class="rs-body">404 的网站、失效的网盘、死掉的博客</div></div>
          <div class="rule-step"><div class="rs-title">无名碑</div><div class="rs-body">什么都不说，只留一块空碑</div></div>
        </div>
      </div>

      <footer class="landing-foot">
        我们不做备份，我们做告别。<br/>
        <span>We don't do backups. We do goodbyes.</span>
      </footer>
    </section>
  `;
}
