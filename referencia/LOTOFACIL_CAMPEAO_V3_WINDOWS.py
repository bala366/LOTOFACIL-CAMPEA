import os,re,csv,random,math,time
from pathlib import Path
from collections import Counter
from itertools import combinations

TITLE='LOTOFACIL CAMPEAO V3 WINDOWS - MOTOR V2 / 300 DUPLAS'
FULL=(1<<25)-1
NUM_RE=re.compile(r'(?<!\d)\d{1,5}(?!\d)')

def arquivos():
    pastas=[Path.home()/'Downloads',Path.home()/'OneDrive'/'Downloads',Path.home()/'Transferências',Path.cwd()]
    seen=set(); found=[]
    for p in pastas:
        if not p.is_dir():continue
        for f in sorted(p.iterdir()):
            if f.is_file() and f.suffix.lower() in ('.txt','.csv') and f.resolve() not in seen:
                seen.add(f.resolve());found.append(f)
    return found

def ler(path):
    text=None
    for enc in ('utf-8-sig','cp1252','latin1'):
        try:text=path.read_text(encoding=enc);break
        except UnicodeError:continue
    if text is None:raise ValueError('Nao foi possivel ler arquivo')
    draws={}; ignored=Counter(); examples=[]
    for ln,line in enumerate(text.splitlines(),1):
        s=line.strip()
        if not s or s.startswith('#') or 'http://' in s.lower() or 'https://' in s.lower():continue
        # Header CSV or TXT: identify contest and the 15 drawn numbers.
        # Supports: contest - 15 comma-separated numbers; contest;date;15 numbers;
        parts=re.split(r'[;,\t|]',s)
        ints=[int(v) for v in NUM_RE.findall(s)]
        candidates=[]
        # First 15 numbers after contest, with optional date fields.
        if len(parts)>=16:
            for start in (1,2,3,4):
                if len(parts)<start+15:continue
                seq=[]
                for field in parts[start:start+15]:
                    v=field.strip()
                    if not re.fullmatch(r'\d{1,2}',v):break
                    seq.append(int(v))
                if len(seq)==15 and len(set(seq))==15 and all(1<=x<=25 for x in seq):
                    first=re.findall(r'\d+',parts[0]);
                    if first:candidates.append((int(first[0]),seq))
        # Format: 1 - 01,02,...15 (separate contest first)
        m=re.match(r'^\s*(\d+)\s*[-:]\s*(.+)$',s)
        if m:
            tail=[int(x) for x in NUM_RE.findall(m.group(2))]
            if len(tail)>=15:
                seq=tail[:15]
                if len(set(seq))==15 and all(1<=x<=25 for x in seq):candidates.append((int(m.group(1)),seq))
        # Plain whitespace: contest + 15 values; optionally date then 15
        if not candidates and len(ints)>=16:
            for start in (1,2,3,4):
                seq=ints[start:start+15]
                if len(seq)==15 and len(set(seq))==15 and all(1<=x<=25 for x in seq):
                    candidates.append((ints[0],seq));break
        if candidates:
            contest,nums=candidates[0]
            if contest>0 and contest not in draws:
                mask=sum(1<<(n-1) for n in nums)
                draws[contest]=FULL^mask
            else:ignored['concurso duplicado/invalido']+=1
        else:
            ignored['cabecalho/linha sem 15 dezenas validas']+=1
            if len(examples)<4:examples.append((ln,s[:95]))
    if not draws:raise ValueError('Nenhum concurso reconhecido. Confira formato do TXT.')
    return sorted(draws.items()),ignored,examples

def histograma(mask,draws):
    hist=[0]*11
    for fail in draws:
        hist[(mask&fail).bit_count()]+=1
    return hist

def main():
    print('\n'+'='*62+'\n'+TITLE+'\n'+'='*62)
    files=arquivos()
    if not files:
        print('Nenhum TXT/CSV encontrado na pasta Download.');return
    for i,f in enumerate(files,1):print(f'{i:2d} - {f.name}')
    try:n=int(input('\nNUMERO DO ARQUIVO: '));path=files[n-1]
    except (ValueError,IndexError):print('Opcao invalida');return
    records,ignored,examples=ler(path)
    draws=[m for _,m in records]
    drawn=[FULL^m for m in draws]
    historical_games=set(drawn)
    print(f'\nCONCURSOS VALIDOS: {len(records)} | PRIMEIRO: {records[0][0]} | ULTIMO: {records[-1][0]}')
    print('LINHAS IGNORADAS:',dict(ignored))
    for a,b in examples:print('  linha',a,':',b)
    if len(records)<30:print('Historico muito curto para avaliar.');return
    gaps=set(range(records[0][0],records[-1][0]+1))-set(x for x,_ in records)
    if gaps:print('ATENCAO: CONCURSOS FALTANTES:',len(gaps),'exemplos:',sorted(gaps)[:15])
    if input('CONTINUAR ANALISE? (S/N): ').strip().upper()!='S':return
    # The latest 100 are given extra importance, but historical data remains counted.
    recent=draws[-100:]
    pair_data=[]; pair_score={}
    for a,b in combinations(range(1,26),2):
        bit=(1<<(a-1))|(1<<(b-1))
        total=sum((d&bit)==bit for d in draws)
        last100=sum((d&bit)==bit for d in recent)
        last20=sum((d&bit)==bit for d in draws[-20:])
        delay=next((i for i,d in enumerate(reversed(draws)) if (d&bit)==bit),len(draws))
        score=total/len(draws)*100+last100*0.5+last20*1.0
        pair_score[(a,b)]=score
        pair_data.append((score,a,b,total,last100,last20,delay))
    pair_data.sort(reverse=True)
    print('\nTOP 20 DUPLAS QUE FALHARAM JUNTAS:')
    for i,(sc,a,b,t,r20,r5,delay) in enumerate(pair_data[:20],1):
        print(f'{i:02d}. {a:02d}-{b:02d} | historico {t} | ult100 {r20} | ult20 {r5} | atraso {delay} | score {sc:.1f}')
    # Filtros aprendidos do historico (nao sao leis matematicas).
    PRIMOS={2,3,5,7,11,13,17,19,23}
    FIB={1,2,3,5,8,13,21}
    BORDA={1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}
    MIOLO=set(range(1,26))-BORDA
    def nbits(m):return m.bit_count()
    def maskset(ns):return sum(1<<(n-1) for n in ns)
    PRIME_MASK=maskset(PRIMOS); FIB_MASK=maskset(FIB)
    BORDER_MASK=maskset(BORDA); CENTER_MASK=maskset(MIOLO)
    EVEN_MASK=maskset(range(2,26,2))
    last_draw=drawn[-1]
    def metrics(game):
        return (nbits(game&last_draw),nbits(game&PRIME_MASK),nbits(game&FIB_MASK),
                nbits(game&BORDER_MASK),nbits(game&CENTER_MASK),nbits(game&EVEN_MASK),
                sum(i+1 for i in range(25) if game>>i&1))
    reference=[metrics(m) for m in drawn]
    def bounds(index,lo=0.03,hi=0.97):
        vals=sorted(v[index] for v in reference)
        return vals[int((len(vals)-1)*lo)],vals[int((len(vals)-1)*hi)]
    # Repetidas com ultimo concurso: priorizar 8,9,10 conforme pedido,
    # mas permitir que o usuario ajuste caso a amostra mostre outro padrao.
    repeat_allowed={8,9,10}
    print('\nFILTROS LOTOFACIL CAMPEAO V2:')
    for label,i in [('Primos',1),('Fibonacci',2),('Borda',3),('Miolo',4),('Pares',5),('Soma',6)]:
        a,b=bounds(i);print(f'  {label}: faixa historica 3%-97% = {a} a {b}')
    counts=Counter(m[0] for m in reference[1:])
    print('  Repetidas com ultimo concurso: 8, 9 ou 10 (configuravel)')
    print('  Observacao: frequencias historicas nao tornam repeticoes impossiveis.')
    change=input('Manter filtros automaticos? (S/N, padrao S): ').strip().upper()
    if change=='N':
        raw=input('Repetidas permitidas, ex. 8,9,10: ').strip()
        try:
            new={int(x.strip()) for x in raw.split(',')}
            if new and all(0<=x<=15 for x in new):repeat_allowed=new
        except ValueError:print('Entrada invalida; mantidos 8,9,10')
    # Penalidade por distancias alem dos quantis observados.
    # Repetidas e jogo exato ja sorteado sao restricoes obrigatorias.
    filter_bounds=[bounds(i) for i in range(1,7)]
    def filter_penalty(game):
        if game in historical_games:return 1000000.0
        m=metrics(game)
        if m[0] not in repeat_allowed:return 1000000.0
        penalty=0.0
        for i,(low,high) in enumerate(filter_bounds,1):
            value=m[i]
            delta=max(low-value,0,value-high)
            penalty+=delta*delta*(1.2 if i==6 else 8.0)
        return penalty
    print('  Jogos identicos a concursos anteriores serao descartados.')

    # Optimize 10-number exclusion set; favor strong pair connections and high partial hits.
    # Training windows: full historical pair strengths + latest 200 drawings for collective score.
    train=draws[-200:]
    def fitness(mask):
        nums=[i+1 for i in range(25) if mask>>i&1]
        pair_strength=sum(pair_score[(a,b)] for a,b in combinations(nums,2))/45
        # Higher-order partial hits are valued more strongly, but not used as guarantees.
        # 6=>1, 7=>3, 8=>10, 9=>35, 10=>120
        weights=(0,0,0,0,0,0,1,3,10,35,120)
        collective=sum(weights[(mask&d).bit_count()] for d in train)/len(train)
        return pair_strength+collective*3-filter_penalty(FULL^mask)
    random.seed(20261012)
    cache={}
    def val(mask):
        if mask not in cache:cache[mask]=fitness(mask)
        return cache[mask]
    # Greedy multi-start hill-climb; bounded CPU suitable for Pydroid.
    best=[];seen=set();start=time.time()
    for restart in range(35):
        if restart<12:
            chosen=set()
            for _,a,b,*_ in pair_data:
                if a not in chosen and b not in chosen and len(chosen)<=8:
                    chosen.update((a,b))
                if len(chosen)==10:break
        else:chosen=set(random.sample(range(1,26),10))
        mask=sum(1<<(x-1) for x in chosen)
        score=val(mask)
        for _ in range(22):
            outside=[i for i in range(25) if not(mask>>i&1)]
            inside=[i for i in range(25) if mask>>i&1]
            candidate=(score,mask)
            for x in inside:
                without=mask^(1<<x)
                for y in outside:
                    new=without|(1<<y)
                    s=val(new)
                    if s>candidate[0]+1e-8:candidate=(s,new)
            if candidate[1]==mask:break
            score,mask=candidate
        if mask not in seen:
            seen.add(mask);best.append((score,mask))
        if restart%10==9:print(f'PROCESSADOS {restart+1}/35 reinicios...')
    best=[(sc,m) for sc,m in best if sc>-100000]
    best.sort(reverse=True)
    if not best:
        print("Nenhum candidato passou pelos filtros. Tente ampliar as repetidas.");return
    print('\nTOP 5 CONJUNTOS DE 10 DEZENAS PARA FALHA:')
    for idx,(sc,mask) in enumerate(best[:5],1):
        nums=[i+1 for i in range(25) if mask>>i&1]
        print(idx,' '.join(f'{n:02d}' for n in nums),'SCORE',round(sc,3))
    print('\nEscolha um dos 5 conjuntos (padrao 1).')
    try:choice=int(input('NUMERO (1-5): ') or '1')-1; score,mask=best[choice] if 0<=choice<min(5,len(best)) else best[0]
    except ValueError:score,mask=best[0]
    nums=[i+1 for i in range(25) if mask>>i&1]
    # Find best 5-pair matching within the selected 10, maximizing pair strengths.
    def pairing(items):
        if not items:return (0,[])
        first=items[0];bestp=(-1e30,[])
        for i in range(1,len(items)):
            second=items[i];sc,rest=pairing(items[1:i]+items[i+1:])
            pair=(min(first,second),max(first,second));sc+=pair_score[pair]
            if sc>bestp[0]:bestp=(sc,[pair]+rest)
        return bestp
    _,pairs=pairing(nums)
    game=[i for i in range(1,26) if i not in nums]
    hist=histograma(mask,draws)
    print('\n'+'='*62+'\nRESULTADO LOTO FACIL CAMPEAO V2')
    for i,(a,b) in enumerate(pairs,1):print(f'DUPLA {i}: {a:02d} - {b:02d}')
    print('10 PARA FALHA:', ' '.join(f'{n:02d}' for n in nums))
    print('15 PARA JOGAR:',' '.join(f'{n:02d}' for n in game))
    print('FILTROS DO JOGO (repetidas, primos, fibonacci, borda, miolo, pares, soma):',metrics(FULL^mask))
    print('JOGO JA SORTEADO ANTES?', 'SIM' if (FULL^mask) in historical_games else 'NAO')
    print('HISTORICO DE FALHAS DO CONJUNTO:')
    for n in range(5,11):print(f'  {n} falhas: {hist[n]} concursos')
    print('TEMPO:',round(time.time()-start,1),'segundos')
    output=Path(__file__).resolve().parent
    folder=output/'RELATORIOS_LOTOFACIL_CAMPEAO_V3';folder.mkdir(exist_ok=True)
    report=folder/'resultado_campeao.txt'
    with report.open('w',encoding='utf-8') as f:
        f.write(TITLE+'\nArquivo: '+path.name+'\nConcursos: '+str(len(draws))+'\n')
        f.write('5 DUPLAS SEM REPETICAO:\n')
        for a,b in pairs:f.write(f'{a:02d}-{b:02d}\n')
        f.write('10 PARA FALHA: '+' '.join(f'{x:02d}' for x in nums)+'\n')
        f.write('15 PARA JOGAR: '+' '.join(f'{x:02d}' for x in game)+'\n')
        f.write('FILTROS (repetidas,primos,fibonacci,borda,miolo,pares,soma): '+str(metrics(FULL^mask))+'\n')
        f.write('Jogo ja sorteado: NAO\n')
        for i,n in enumerate(hist):f.write(f'{i} falhas: {n}\n')
        f.write('\nTOP 5 CONJUNTOS:\n')
        for sc,m in best[:5]:f.write(f'{sc:.3f} | '+ ' '.join(f'{i+1:02d}' for i in range(25) if m>>i&1)+'\n')
    with (folder/'ranking_300_duplas.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['dupla','historico','ultimos_100','ultimos_20','atraso','score'])
        for sc,a,b,t,r100,r20,delay in pair_data:w.writerow([f'{a:02d}-{b:02d}',t,r100,r20,delay,f'{sc:.3f}'])
    gerar_pdf(folder, path, records, pair_data, pairs, nums, game, hist, metrics(FULL^mask), best[:5], score)
    print('\nRELATORIOS SALVOS EM:',folder)
    try:
        if os.name=='nt':os.startfile(folder)
    except OSError:pass
    print('ATENCAO: resultados historicos nao garantem acertos futuros.')

def gerar_pdf(folder, origem, records, pair_data, pairs, falhas, jogo, hist, filtros, melhores, score):
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase.pdfmetrics import stringWidth
    pdf=folder/'LOTOFACIL_CAMPEAO_V3_RELATORIO_E_VOLANTE.pdf'
    c=canvas.Canvas(str(pdf),pagesize=A4)
    W,H=A4
    PURPLE=HexColor('#64249A'); LIGHT=HexColor('#F1E8F8'); DARK=HexColor('#2B1641'); GREEN=HexColor('#D8F6D7')
    def txt(x,y,t,size=10,color=DARK,bold=False):
        c.setFillColor(color);c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.drawString(x,y,str(t))
    def header(label):
        c.setFillColor(PURPLE);c.rect(0,H-83,W,83,fill=1,stroke=0)
        txt(35,H-42,'LOTOFACIL CAMPEAO V3 - WINDOWS',20,white,True)
        txt(35,H-64,label,10,white)
    header('PAGINA 1 DE 2 | RELATORIO DO MOTOR V2')
    txt(35,H-110,'HISTORICO ANALISADO',13,PURPLE,True)
    txt(35,H-130,'Arquivo: '+origem.name[:76],9)
    txt(35,H-147,f'Concursos: {len(records)}  |  Primeiro: {records[0][0]}  |  Ultimo: {records[-1][0]}',10)
    txt(35,H-177,'5 DUPLAS CAMPEAS SEM REPETIR DEZENAS',12,PURPLE,True)
    for i,(a,b) in enumerate(pairs,1):
        x=35+(i-1)*106
        c.setFillColor(LIGHT);c.roundRect(x,H-219,99,29,5,fill=1,stroke=0)
        txt(x+8,H-209,f'{i}: {a:02d} - {b:02d}',11,PURPLE,True)
    txt(35,H-249,'10 DEZENAS PARA FALHA',11,PURPLE,True)
    txt(35,H-269,'  '.join(f'{x:02d}' for x in falhas),13,DARK,True)
    txt(35,H-300,'15 DEZENAS PARA JOGAR',11,PURPLE,True)
    txt(35,H-320,'  '.join(f'{x:02d}' for x in jogo),12,DARK,True)
    txt(35,H-350,'FILTROS DO JOGO',11,PURPLE,True)
    names=['Repetidas','Primos','Fibonacci','Borda','Miolo','Pares','Soma']
    txt(35,H-368,' | '.join(f'{n}: {v}' for n,v in zip(names,filtros)),8.3)
    txt(35,H-394,'HISTORICO DE FALHAS DO CONJUNTO',11,PURPLE,True)
    for i,n in enumerate(range(5,11)):
        txt(35+(i%3)*174,H-416-(i//3)*19,f'{n} falhas: {hist[n]} concursos',9)
    txt(35,H-479,'TOP 5 CONJUNTOS DE 10 PARA FALHA',11,PURPLE,True)
    for i,(sc,m) in enumerate(melhores,1):
        numbers=' '.join(f'{n:02d}' for n in range(1,26) if m>>(n-1)&1)
        txt(35,H-501-(i-1)*19,f'{i}. {numbers}   score {sc:.2f}',9)
    txt(35,H-624,'TOP 5 DUPLAS INDIVIDUAIS (DAS 300)',11,PURPLE,True)
    for i,(sc,a,b,total,r100,r20,delay) in enumerate(pair_data[:5],1):
        txt(35,H-646-(i-1)*17,f'{i}. {a:02d}-{b:02d}  |  historico {total}  |  ult100 {r100}  |  ult20 {r20}  |  atraso {delay}  |  score {sc:.1f}',8.5)
    txt(35,30,'Estudo estatistico historico: nao garante acertos futuros.',8)
    c.showPage()
    header('PAGINA 2 DE 2 | VOLANTE ROXO CIRCULADO')
    txt(35,H-111,'JOGO COM 15 DEZENAS MARCADAS',15,PURPLE,True)
    txt(35,H-135,'Circulos roxos = dezenas para jogar | Cinza = dezenas para falha',9)
    selected=set(jogo)
    side=75;cell=89;top=H-204
    for row in range(5):
        for col in range(5):
            n=row*5+col+1;x=side+col*cell;y=top-row*87
            c.setFillColor(LIGHT if n in selected else HexColor('#F5F5F5'))
            c.setStrokeColor(PURPLE if n in selected else HexColor('#B9B9B9'))
            c.setLineWidth(3 if n in selected else 1)
            c.circle(x+19,y,29,fill=1,stroke=1)
            txt(x+4,y-6,f'{n:02d}',18,PURPLE if n in selected else HexColor('#888888'),True)
    c.setFillColor(LIGHT);c.roundRect(35,115,W-70,70,8,fill=1,stroke=0)
    txt(48,162,'15 DEZENAS DO JOGO',12,PURPLE,True)
    txt(48,140,'  '.join(f'{x:02d}' for x in jogo),13,DARK,True)
    txt(35,88,'10 DEZENAS EXCLUIDAS: '+'  '.join(f'{x:02d}' for x in falhas),9)
    txt(35,59,'5 DUPLAS: '+'  |  '.join(f'{a:02d}-{b:02d}' for a,b in pairs),9)
    txt(35,30,'Volante ilustrativo. Confira as dezenas antes de registrar a aposta.',8)
    c.save()
    print('PDF 2 PAGINAS GERADO:',pdf)

if __name__=='__main__':
    try:main()
    except Exception as e:
        import traceback;traceback.print_exc()
    input('\nENTER PARA SAIR...')
