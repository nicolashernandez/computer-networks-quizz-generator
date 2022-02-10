# Nicolas Hernandez 2019
# GPLv2 Licence https://docs.moodle.org/19/fr/Licence
#
# IPv4 subnet generator and quizz generator with [XML Moodle output format support](https://docs.moodle.org/3x/fr/Question_cloze_à_réponses_intégrées)
# Works with `python3`.
#
# To use it
# - edit and select whether you want to generate a quizz with hints (e.g. `wi_hints = True`), and the number of questions to generate (e.g. `max_questions = 100`)
# Then 
#  
#    python3 generate-ipv4-subnets-and-quizz.py > xml-mooddle-quizz_100-train.xml # wi_hints = True 
#
# Or
#
#    python3 generate-ipv4-subnets-and-quizz.py > xml-mooddle-quizz_100-test.xml # wi_hints = False


from random import *


def dec_to_bin(d):
  #bin_value = bin(generate_ipv4_address())
  #
  #     if n==0: return ''
  #     else:
  #         return dec_to_bin(n/2) + str(n%2)
  return "{0:b}".format(d)

def generate_ipv4_address_bin():
    d = randint(1,2**32) # importance d'avoir 32 bits donc pas une bonne solution à moins de bufferiser
    b = dec_to_bin(d)
    #print ("debug:"+ b)
    b = '0'* int(32-len(b)) + b
    #print ("debug:"+ b)
    return b

def get_address_class(b):
  address_class = "unk"
  if b.startswith("0"): return "A"
  if b.startswith("10"): return "B"
  if b.startswith("110"): return "C"
  return address_class

def bin_to_dec(b):
  return str(int(b, 2))

def pretty_dotted_bin(b):
  return b[0:4]+' '+ b[4:8]+ ' . '+ b[8:12]+' '+ b[12:16]+ ' . '+  b[16:20]+' '+ b[20:24]+ ' . '+ b[24:28]+' '+ b[28:32]

def pretty_dotted_dec(n):
  return bin_to_dec(n[0:8])+'.'+bin_to_dec(n[8:16])+'.'+bin_to_dec(n[16:24])+'.'+bin_to_dec(n[24:32])

def dotted_dec_to_bin (d):
  octets = d.split ('.')
  print (octets)
  #bin_ip = list()
  bin_ip = ""
  for o in octets:
    bin_o = dec_to_bin(int(o))
    bin_ip += '0'* int(8-len(bin_o)) + bin_o
    #bin_ip.append('0'* int(8-len(bin_o)) + bin_o)
  print (bin_ip)  
  return str(bin_ip) # '.'.join(bin_ip)

def split_dotted_dec_cidr (d):
  elements = d.split ('/')  
  return elements[0], int(elements[1])

def generate_mask_cidr():
    # on s'interdit 32 (classe D), 31 (peu de sens), 0 (adresse d'initialisation)
    #n = randint(1,30)
    #24  256
    #23  512
    #22  1024
    #21  2048
    #20  4096 
    n = randint(4,28)
    return n

def network_id (ipv4_address_bin, mask):
  return ipv4_address_bin[0:mask]

#def machine_id (ipv4_address_bin, mask):

def get_network_address_bin (ipv4_address_bin, mask):
  return network_id (ipv4_address_bin, mask)+ '0'* int(32-mask)

def get_broadcast_address_bin (ipv4_address_bin, mask):
  return network_id (ipv4_address_bin, mask)+ '1'* int(32-mask)

def is_network_address_bin (ipv4_address_bin, mask):
  return ipv4_address_bin == get_network_address_bin (ipv4_address_bin, mask)

def is_broadcast_address_bin (ipv4_address_bin, mask):
  return ipv4_address_bin == get_broadcast_address_bin (ipv4_address_bin, mask)

def is_host_address_bin (ipv4_address_bin, mask):
  return not (is_network_address_bin(ipv4_address_bin, mask) or is_broadcast_address_bin(ipv4_address_bin, mask)) 


def get_first_host_address_bin (ipv4_address_bin, mask):
  #print (network_id (ipv4_address_bin, mask))
  #print ('0' * int(32-(mask+1)))
  #print ('0' * int(32-(mask)))
  #print (1 * '1')
  return '{}{}{}'.format(network_id (ipv4_address_bin, mask), '0' * int(32-(mask+1)), 1 * '1')

def get_last_host_address_bin (ipv4_address_bin, mask):
  return '{}{}{}'.format(network_id (ipv4_address_bin, mask), '1' * int(32-(mask+1)), 1 * '0')


def hosts_length (mask):
  return (2**(32-mask))-2

def pretty_hosts_length (mask):
  return "2^"+str(32-mask)+"-2"  

def is_private_address (ipv4_address_bin, address_class):
  if address_class == 'A':
    # 10.0.0.0 - 10.255.255.255
    if ipv4_address_bin.startswith('00001010'): return True
  else:
    if address_class == 'B':
      # 172.16.0.0 - 172.31.255.255
      if ipv4_address_bin.startswith('10101100') and int("{0:b}".format(0), 2) <= int(ipv4_address_bin[8:16], 2) and int("{0:b}".format(31), 2) >= int(ipv4_address_bin[8:16], 2):
        return True
    else:
      if address_class == 'C':
      # 192.168.0.0 - 192.168.255.255 
        if ipv4_address_bin.startswith('1100000010101000'):
          #and int("{0:b}".format("0"), 2) <= int(ipv4_address_bin[8:16], 2)
          #and int("{0:b}".format("31"), 2) >= int(ipv4_address_bin[8:16], 2):
          return True
  return False  

def get_mask_bin(mask_cidr):
  return '{}{}'.format(mask_cidr * '1', '0' * int(32-(mask_cidr)))

def mask_dec(mask_cidr):
  return pretty_dotted_dec(get_mask_bin(mask_cidr))

def generate_close_host(ipv4_address_bin, mask_cidr):
  id = network_id (ipv4_address_bin, mask_cidr)
  id = id[0:len(id)-1] # -1 on tire aléatoire un nombre si premier bit tiré est identique à celui supprimé alors appartiendra et sinon non...
  nb_bits_machine_plus_1 = 32- len(id)
  d = randint(1,2**(nb_bits_machine_plus_1)) # importance d'avoir 32 bits donc pas une bonne solution à moins de bufferiser
  b = dec_to_bin(d)
  #print ("debug:"+ b)
  b = id + b + '0'* int(32- (len(id) + len(b)) -1) + '1' 
  return b

def are_on_the_same_network(ad1, ad2, mask_cidr):
  return ad1[0:mask_cidr] == ad2[0:mask_cidr]


def debug(ipv4_address_bin, mask_cidr, ipv4_address_dec_pte, address_class, network_address_bin, broadcast_address_bin, first_host_address_bin, last_host_address_bin, close_host_bin, close_host_dec_pte):

  #print(ipv4_address_bin)
  print("@ip binaire pointée\t\t"+pretty_dotted_bin(ipv4_address_bin))
  #print (ipv4_address_bin[0:8])
  print("@ip décimal pointée\t\t"+ipv4_address_dec_pte)

  print("address_class\t"+address_class)

  print ("is private ", is_private_address(ipv4_address_bin, address_class))
  print ("is network_address", is_network_address_bin(ipv4_address_bin, mask_cidr))
  print ("is broadcast_address", is_broadcast_address_bin(ipv4_address_bin, mask_cidr))
  print ("is host_address", is_host_address_bin(ipv4_address_bin, mask_cidr))

  print("mask_cidr\t"+str(mask_cidr))
  print ("mask_dec\t"+mask_dec(mask_cidr))


  print("@réseau binaire pointée\t\t"+pretty_dotted_bin(network_address_bin))
  print("@réseau décimal pointée\t\t"+pretty_dotted_dec(network_address_bin))


  print("@diffusion binaire pointée\t"+pretty_dotted_bin(broadcast_address_bin))
  print("@diffusion décimal pointée\t"+pretty_dotted_dec(broadcast_address_bin))

  print("#hosts\t"+str(hosts_length(mask_cidr)))
  print("#hosts\t"+str(pretty_hosts_length(mask_cidr)))

  print ("plage d'adresse")


  print("@de binaire pointée\t\t"+pretty_dotted_bin(first_host_address_bin))
  print("@de décimal pointée\t\t"+pretty_dotted_dec(first_host_address_bin))
  print("@à binaire pointée\t\t"+pretty_dotted_bin(last_host_address_bin))
  print("@à décimal pointée\t\t"+pretty_dotted_dec(last_host_address_bin))

  print("@close host binaire pointée\t"+pretty_dotted_bin(close_host_bin))
  print("@close host décimal pointée\t"+pretty_dotted_dec(close_host_bin))
  
  print()


def generate_plan ():
  ipv4_address_bin = generate_ipv4_address_bin()
  mask_cidr = generate_mask_cidr()

  # d 172.17.2.17 ; B /16 privé ; machine 
  # i 10.255.255.255 ; A /8 ; privée (10...) ; adresse de diffusion
  # e 172.32.9.2 ; B /16 publique ; machine

  #ipv4_address_dotted_dec = "172.17.2.17"
  #mask_cidr = 16
  # SET
  #ipv4_address_dotted_dec, mask_cidr = split_dotted_dec_cidr("192.168.123.202/23") 
  #ipv4_address_dotted_dec, mask_cidr = split_dotted_dec_cidr("128.201.168.143/27")
  #ipv4_address_bin = dotted_dec_to_bin(ipv4_address_dotted_dec)
    
  ipv4_address_dec_pte = pretty_dotted_dec(ipv4_address_bin)
  address_class = get_address_class(ipv4_address_bin)

  network_address_bin = get_network_address_bin(ipv4_address_bin, mask_cidr)
  broadcast_address_bin = get_broadcast_address_bin(ipv4_address_bin, mask_cidr)
  first_host_address_bin = get_first_host_address_bin(ipv4_address_bin, mask_cidr)
  last_host_address_bin = get_last_host_address_bin(ipv4_address_bin, mask_cidr)

  close_host_bin = generate_close_host(ipv4_address_bin, mask_cidr)
  close_host_dec_pte = pretty_dotted_dec(close_host_bin)

  #debug(ipv4_address_bin, mask_cidr, ipv4_address_dec_pte, address_class, network_address_bin, broadcast_address_bin, first_host_address_bin, last_host_address_bin, close_host_bin, close_host_dec_pte)

  question = list()
  if address_class in ['A', 'B', 'C']:
    if wi_html:question.append ('<question type="cloze"><name><text>cloze plan '+ipv4_address_dec_pte+"/"+str(mask_cidr)+'</text></name><questiontext format="html"><text><![CDATA[<p>')
    else: question.append ("\n")

    question.append ("Soit l'adresse IP et le masque suivants : "+ipv4_address_dec_pte+"/"+str(mask_cidr)+".")
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")

    question.append ("En décimal pointée (W.X.Y.Z) le masque CIDR aurait pour valeur {1:SHORTANSWER:%100%"+mask_dec(mask_cidr)+"}.")
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")

    if address_class == 'A':
      #question.append ("Dans le système de classe, cette adresse serait de classe (A, B ou C) : {1:SHORTANSWER:%100%"+address_class+"} ")
      question.append ("Si le système de classes était toujours d'actualités, cette adresse serait de classe {1:MC:%100%A~B~C} (A, B ou C).")
    else:
      if address_class == 'B':
        question.append ("Si le système de classes était toujours d'actualités, cette adresse serait de classe {1:MC:A~%100%B~C} (A, B ou C).")
      else:
        if address_class == 'C':
          question.append ("Si le système de classes était toujours d'actualités, cette adresse serait de classe {1:MC:A~B~%100%C} (A, B ou C).")   
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")

    if is_private_address(ipv4_address_bin, address_class):
      question.append ("Cette adresse est {1:MC:%100%privée~publique} (privée ou publique).")
    else:
      question.append ("Cette adresse est {1:MC:privée~%100%publique} (privée ou publique).")
    if wi_html:  question.append ("<br>")  
    else: question.append ("\n")

    if is_network_address_bin(ipv4_address_bin, mask_cidr):
      question.append ("Cette adresse est une adresse de {1:MC:%100%réseau~diffusion~machine} (réseau, diffusion, machine).")
    else:
      if is_broadcast_address_bin(ipv4_address_bin, mask_cidr):
        question.append ("Cette adresse est une adresse de {1:MC:réseau~%100%diffusion~machine} (réseau, diffusion, machine).")
      else:
        if is_host_address_bin(ipv4_address_bin, mask_cidr):
          question.append ("Cette adresse est une adresse de {1:MC:réseau~diffusion~%100%machine} (réseau, diffusion, machine).")
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")
    
    question.append ("L'adresse réseau est {1:SHORTANSWER:%100%"+pretty_dotted_dec(network_address_bin)+"} (en décimal pointée W.X.Y.Z).")
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")

    question.append ("L'adresse de diffusion est {1:SHORTANSWER:%100%"+pretty_dotted_dec(broadcast_address_bin)+"} (en décimal pointée W.X.Y.Z).")  
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")
    
    question.append ("Sur ce réseau, on peut adresser {1:SHORTANSWER:%100%"+str(hosts_length(mask_cidr))+"} machines.")
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")

    question.append ("L'adresse IP de la première machine adressable est {1:SHORTANSWER:%100%"+pretty_dotted_dec(first_host_address_bin)+"} (en décimal pointée W.X.Y.Z).")
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")

    question.append ("L'adresse IP de la dernière machine adressable est {1:SHORTANSWER:%100%"+pretty_dotted_dec(last_host_address_bin)+"} (en décimal pointée W.X.Y.Z).")
    if wi_html:  question.append ("<br>")
    else: question.append ("\n")

    if are_on_the_same_network(ipv4_address_bin, close_host_bin, mask_cidr):
      question.append ("Est ce que l'adresse IP "+close_host_dec_pte+" se trouve sur le même réseau ? {1:MC:%100%oui~non} (oui ou non).")
    else:
      question.append ("Est ce que l'adresse IP "+close_host_dec_pte+" se trouve sur le même réseau ? {1:MC:oui~%100%non} (oui ou non).")
    if wi_html:  question.append ('<br><br></p>]]></text></questiontext><generalfeedback format="html"><text><![CDATA[<p>')
    
    if wi_hints: 
      #print(ipv4_address_bin)
      question.append("@IP en binaire pointée\t\t:"+pretty_dotted_bin(ipv4_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      #print (ipv4_address_bin[0:8])
      question.append("@IP en décimal pointée\t\t:"+ipv4_address_dec_pte)
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append("Classe d'adresse : \t"+address_class)
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append ("Est privée : "+ str(is_private_address(ipv4_address_bin, address_class)))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append ("Est une adresse réseau : "+ str(is_network_address_bin(ipv4_address_bin, mask_cidr)))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append ("Est une adresse de diffusion : "+ str(is_broadcast_address_bin(ipv4_address_bin, mask_cidr)))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append ("Est une adresse machine : "+ str(is_host_address_bin(ipv4_address_bin, mask_cidr)))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append("Le masque en notation CIDR est \t:"+str(mask_cidr))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append("Le masque en binaire pointée est \t:"+pretty_dotted_bin(get_mask_bin(mask_cidr)))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append ("Le masque en décimal pointée est \t:"+mask_dec(mask_cidr))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")




      question.append("@réseau en binaire pointée\t\t:"+pretty_dotted_bin(network_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append("@réseau en décimal pointée\t\t:"+pretty_dotted_dec(network_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")


      question.append("@diffusion en binaire pointée\t:"+pretty_dotted_bin(broadcast_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append("@diffusion en décimal pointée\t:"+pretty_dotted_dec(broadcast_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append("#hosts\t"+str(pretty_hosts_length(mask_cidr))+' = '+str(hosts_length(mask_cidr)))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append ("Plage d'adresse :")
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append("@de en binaire pointée\t\t:"+pretty_dotted_bin(first_host_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append("@de en décimal pointée\t\t:"+pretty_dotted_dec(first_host_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append("@à en binaire pointée\t\t:"+pretty_dotted_bin(last_host_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append("@à en décimal pointée\t\t:"+pretty_dotted_dec(last_host_address_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append("@IP autre machine en binaire pointée\t:"+pretty_dotted_bin(close_host_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      question.append("@IP autre machine en décimal pointée\t:"+pretty_dotted_dec(close_host_bin))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append ("Sont sur le même réseau : " +str(are_on_the_same_network(ipv4_address_bin, close_host_bin, mask_cidr)))
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

    if wi_html:  question.append ('</p>]]></text></generalfeedback><penalty>0.3333333</penalty><hidden>0</hidden>')
    else: question.append ("\n")
  
  


    if wi_hints: 
      # indice 1 : donne les versions binaires
      if wi_html:  question.append ('<hint format="html"><text><![CDATA[<p>')
      else: question.append ("\n")

      question.append ("Le principe général est de tout convertir en binaire, de faire les calculs en binaires puis de rendre les résultats en décimal.")      
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("L'adresse IP en décimal pointée "+ipv4_address_dec_pte+" se convertit en binaire en "+pretty_dotted_bin(ipv4_address_bin)+".")
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("Pour connaître la classe d'adresses (système qui n'existe plus aujourd'hui et qui a été remplacé par la notation CIDR), il faut regarder la valeur binaire du 1er octet. Si le préfixe binaire (les bits de poids forts) est 0 alors c'est de classe A. Si 10 alors de classe B. Si 110 alors de classe C.")
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("Dans chaque classe, au moins une adresse de réseau (et toutes les adresses des machines sur ce réseau) a été réservée pour un usage privé (cad n'existe pas sur Internet). En classe A, 10.0.0.0 - 10.255.255.255. En classe B, 172.16.0.0 - 172.31.255.255. En classe C, 192.168.0.0 - 192.168.255.255") 
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("Une adresse IP compte dans sa partie bit de poids fort (à gauche) l'identifiant du réseau et dans sa partie bit de poids faible (à droite) l'identifiant de la machine sur ce réseau. Le masque permet de déterminer la partie de l'adresse IP qui est réservée pour identifier le réseau et celle qui sert pour identifier la machine sur ce réseau. Par définition, un masque a les bits de la partie réseau à 1 et les bits de la partie machine à 0. Il peut être exprimé en notation CIDR (avec un slash suivi d'une valeur décimal qui indique le nombre de bits de poids fort utilisés pour coder l'identifiant réseau), on peut aussi transcrire la valeur du masque en décimal pointée (W.X.Y.Z).")  
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("Pour déterminer l'adresse réseau (qui désigne le réseau), on fait un 'et logique' entre le masque et l'adresse IP en focus. Ou bien on met à zéro tous les bits de la partie machine de l'IP en focus.")
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("Pour déterminer l'adresse de diffusion (qui permet d'adresser toutes les machines de ce réseau), on met à un tous les bits de la partie machine de l'adresse IP en focus.")
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("Pour déterminer si on est en présence d'une adresse IP d'une machine, il s'agit de vérifier que l'adresse n'est ni une adresse de réseau ni une adresse de diffusion.") 
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")

      question.append ("Le nombre de machines adressables sur un réseau dépend du nombre de bits alloués à la partie machine sur l'adresse IP (soit '32-masque'). Cela se calcule à l'aide de la formule (2^(32-masque))-2. Le '-2' correspond aux adresses réseau et de diffusion qui ne peuvent être utilisés pour adresser une machine.")
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("La plage d'adresses machines adressables s'étend de 'l'adresse réseau plus 1' en binaire à 'l'adresse de diffusion moins 1' en binaire.")
      if wi_html:  question.append ("<br>")
      else: question.append ("\n")
      
      question.append ("Pour déterminer si une machine est sur un réseau ou si deux machines sont sur le même réseau, alors on observe la partie réseau de ces IP. Si elle est identique, ces machines sont censées être sur le même réseau.")
      if wi_html: question.append ("<br>")
      else: question.append ("\n")
      
      if wi_html:  question.append ('</p>]]></text>')
      if wi_html:  question.append ('</hint>')

      # indice 2 : indique où il y a une erreur
      if wi_html:  question.append ('<hint format="html"><text><![CDATA[<p>')
      if wi_html:  question.append ('<br></p>]]></text>')
      if wi_html:  question.append ('<shownumcorrect/>')
      if wi_html:  question.append ('<clearwrong/>')
      if wi_html:  question.append ('</hint>')

    if wi_html:  question.append ('</question>')
    else: question.append ("\n")
    return question
  #print ("Dans le système de classe, cette adresse serait de classe: {1:MCS:=A#Bonne réponse~Arizona#Mauvaise réponse}")
  #    Appariez les villes et les états :
  #    San Francisco: {1:MCS:=Californie#Bonne réponse~Arizona#Mauvaise réponse}
  #    Tucson: {1:MCS:Californie#Mauvaise réponse~%100%Arizona#Bonne réponse}
  #    Los Angeles: {1:MCS:=Californie#Bonne réponse~Arizona#Mauvaise réponse}
  #    Phoenix: {1:MCS:%0%Californie#Mauvaise réponse~=Arizona#Bonne réponse}
  # La capitale de la France est {1:SHORTANSWER:%100%Paris#Bravo!~%50%Marseille#Non, c'est la deuxième plus grande ville de France (après Paris).~*#Mauvaise réponse. La capitale de la France est Paris, bien sûr.}.
  # 23+ 0.8 = {2:NUMERICAL:=23.8:0.1#Rétroaction pour la réponse correcte~%50%23.8:2#Rétroaction pour la réponse valant la moitié des points}.</pre>
  # Ces trois questions seraient intégrées dans UNE SEULE question cloze. (Sans sauts de ligne entre les { } !) 


count = 0
# SET
max_questions = 100
wi_feedback = True # not implemented
wi_hints = False  
wi_html = True # True for xml moodle format export

if wi_html:print ('<?xml version="1.0" encoding="UTF-8"?><quiz><!-- question: 0  --><question type="category"><category><text>top</text></category></question><!-- question: 0  --><question type="category"><category><text>top/Défaut pour M2102</text></category></question>')


while count < max_questions:
  question = generate_plan()
  if (question != None):
    #print ("no question")
    print (''.join(question))
    count +=1

    
if wi_html:print ('</quiz>') 
