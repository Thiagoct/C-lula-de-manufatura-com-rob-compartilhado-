import random

# ==========================================
# PARÂMETROS GERAIS DA REDE DE PETRI
# ==========================================
NUM_CELULAS = 3
CAPACIDADE_BUFFER_LOCAL = 2
CAPACIDADE_BUFFER_GLOBAL = 4
MAX_CARGA_GLOBAL = 2      # Capacidade MÁXIMA do robô global
PASSOS_SIMULACAO = 15
CHANCE_CONCLUSAO = 0.20    # Probabilidade de uma máquina terminar o processamento no ciclo

class Maquina:
    def __init__(self, id_maq, id_celula):
        self.id = id_maq
        self.id_celula = id_celula
        self.free = True
        self.proc = False
        self.wait = False

    def tick(self):
        # M_T1: De Livre para Processando
        if self.free:
            self.free = False
            self.proc = True
            print(f"  [{self.id}_T1] Célula {self.id_celula}: {self.id} iniciou o processamento.")
            return

        # M_T2: Fim do tempo indeterminado de processamento
        if self.proc and random.random() < CHANCE_CONCLUSAO:
            self.proc = False
            self.wait = True
            print(f"  [{self.id}_T2] Célula {self.id_celula}: {self.id} finalizou a peça e aguarda o robô.")

class CelulaManufatura:
    def __init__(self, id_celula):
        self.id_celula = id_celula
        self.m1 = Maquina("M1", id_celula)
        self.m2 = Maquina("M2", id_celula)
        
        # Robô Local
        self.r_free = True
        self.r_mov = False
        
        # Buffer Local (Esteira)
        self.b_vagas = CAPACIDADE_BUFFER_LOCAL
        self.b_units = 0

    def tick(self):
        # Atualiza o estado das máquinas
        self.m1.tick()
        self.m2.tick()

        # R_T3: Robô local deposita no buffer
        if self.r_mov and self.b_vagas > 0:
            self.b_vagas -= 1
            self.b_units += 1
            self.r_mov = False
            self.r_free = True
            print(f"  [R_T3] Célula {self.id_celula}: Robô local depositou peça no buffer. (Vagas: {self.b_vagas}, Peças: {self.b_units})")

        # R_T1 / R_T2: Robô local coleta da máquina
        if self.r_free:
            if self.m1.wait:
                self.m1.wait = False
                self.m1.free = True # Loop de reset (M1_T3)
                self.r_free = False
                self.r_mov = True
                print(f"  [R_T2] Célula {self.id_celula}: Robô local coletou peça da M1 e M1_T3 liberou a máquina.")
            elif self.m2.wait:
                self.m2.wait = False
                self.m2.free = True # Loop de reset (M2_T3)
                self.r_free = False
                self.r_mov = True
                print(f"  [R_T1] Célula {self.id_celula}: Robô local coletou peça da M2 e M2_T3 liberou a máquina.")

class Fabrica:
    def __init__(self):
        self.celulas = [CelulaManufatura(i) for i in range(NUM_CELULAS)]
        
        # Robô Global agora tem uma variável de carga dinâmica
        self.g_free = True
        self.g_mov = False
        self.g_carga = 0
        
        # Depósito Global
        self.g_vagas = CAPACIDADE_BUFFER_GLOBAL
        self.g_units = 0

    def tick_global(self):
        # Atualiza todas as células instanciadas
        for celula in self.celulas:
            celula.tick()

        # G_T4 (Transição de Depósito): Robô global deposita no buffer global
        # Só deposita se houver vagas suficientes para a carga atual
        if self.g_mov and self.g_vagas >= self.g_carga:
            self.g_vagas -= self.g_carga
            self.g_units += self.g_carga
            print(f"  [G_T4] Robô Global descarregou {self.g_carga} peça(s) no Depósito. (Vagas GLB: {self.g_vagas}, Peças GLB: {self.g_units})")
            
            # Reseta o estado do robô global
            self.g_mov = False
            self.g_free = True
            self.g_carga = 0

        # G_T1 / G_T2 / G_T3: Robô global inspeciona buffers locais
        elif self.g_free:
            for celula in self.celulas:
                # Se a célula tem pelo menos 1 peça, o robô vai coletar
                if celula.b_units > 0:
                    # Define se vai pegar 1 ou 2 peças (o que for menor entre a capacidade máxima e o disponível)
                    qtd_coletada = min(MAX_CARGA_GLOBAL, celula.b_units)
                    
                    celula.b_units -= qtd_coletada
                    celula.b_vagas += qtd_coletada
                    
                    self.g_carga = qtd_coletada
                    self.g_free = False
                    self.g_mov = True
                    
                    print(f"  [G_T{celula.id_celula + 1}] Robô Global coletou {qtd_coletada} peça(s) do Buffer da Célula {celula.id_celula}.")
                    break 

    def imprimir_estado(self, ciclo):
        print(f"--- ESTADO AO FINAL DO CICLO {ciclo} ---")
        for i, c in enumerate(self.celulas):
            print(f"Célula {i} | Buffer: {c.b_units} peças, {c.b_vagas} vagas | "
                  f"M1 Wait: {c.m1.wait} | M2 Wait: {c.m2.wait}")
        print(f"Robô Global  | Em Movimento: {self.g_mov} | Carga Atual: {self.g_carga}")
        print(f"Depósito GLB | Peças: {self.g_units}, Vagas: {self.g_vagas}")
        print("=" * 60)

# ==========================================
# EXECUÇÃO DA SIMULAÇÃO
# ==========================================
if __name__ == "__main__":
    fabrica = Fabrica()
    print("Iniciando simulação de Sistemas a Eventos Discretos...\n")
    print("=" * 60)
    
    for ciclo in range(1, PASSOS_SIMULACAO + 1):
        print(f"CICLO {ciclo} - TRANSICOES DISPARADAS:")
        fabrica.tick_global()
        fabrica.imprimir_estado(ciclo)