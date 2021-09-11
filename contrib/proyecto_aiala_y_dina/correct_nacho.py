# -*- coding: utf-8 -*-

#from dotenv import load_dotenv
#load_dotenv()

import os
import time
import argparse

import numpy as np
import distance
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import cess_esp

from modules.preprocessor import Preprocessor
from modules.postprocessor import Postprocessor
from modules.language_model import LanguageModel
from modules.process_format_errors import ProcessFormatError
import helpers.final_text_generator as text_generator
import modules.results_evaluator as results_evaluator
from symspellpy.symspellpy import SymSpell, Verbosity

import helpers.file as fh
import helpers.utils as utils
import config

# ------------------------------------------------------------------------------------#

if __name__ == '__main__':
    ######################## ARGUMENTOS DE LINEA DE COMANDOS #########################
    ##### datadir = donde están los archivos, list = lista de archivos a scorear #####
    ##################################################################################
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt-prefix", type=str, default="",
                    help="path prefix  where to find ground truth files")
    ap.add_argument("--trans-prefix", type=str, default="",
                    help="path prefix  where to find transcription files")
    ap.add_argument("--list", type=str, default="",
                    help="text file where input files are specified")
    ap.add_argument("--outdir", type=str, default=".",
                    help="output directory.")
    ap.add_argument("--gt-suffix", type=str, default=".gt.txt",
                    help="Suffix of ground truth files.")
    ap.add_argument("--trans-suffix", type=str, default=".txt",
                    help="Suffix of transcribed text files.")

    ################################# INICIALIZACIÓN #################################
    #
    # check args
    #
    args = vars(ap.parse_args())
    print(args)
    gt_prefix = args["gt_prefix"]
    trans_prefix = args["trans_prefix"]
    gt_suffix = args["gt_suffix"]
    trans_suffix = args["trans_suffix"]
    out_dir = args["outdir"]
    list_fname = args["list"]
    #
    #
    #
    #dir_step_1 = 'local_step_1_outputs'
    #dir_step_2 = 'local_step_2_outputs'
    #dir_ocr_outputs = 'local_tesseract_training_outputs'
    #dir_ground_truth = 'local_luisa_traductions'
    #dir_results_evaluation = 'local_results_evaluation'

    #
    # setup corrector
    #
    language_model = LanguageModel()
    language_model.load_model()
    postprocessor = Postprocessor()
    #process_format_error = ProcessFormatError(postprocessor, language_model)
    postprocessor.load_vocabulary(config.vocabulary)

    #
    # process all files in list
    #
    scores = list()
    with open(list_fname) as list_file:
        score_dict = dict()
        n = 0
        for relfname in list_file:
            n += 1
            #
            # nombres de archivos y directorios de entrada y salida
            #
            relfname = relfname.rstrip('\n')
            reldir, fname = os.path.split(relfname)
            fbase, fext = os.path.splitext(fname)

            trans_dir = os.path.join(trans_prefix, reldir)
            gt_dir = os.path.join(gt_prefix, reldir)

            trans_fname = os.path.join(trans_dir, fbase + trans_suffix)
            gt_fname = os.path.join(gt_dir, fbase + gt_suffix)
            if 0:
                print(f'#{n} image={relfname} trans={trans_fname} gt_fname={gt_fname} ', end='')
            else:
                print(f'{relfname:40s}', end=' | ')

            #
            # ground truth
            #
            ftxt = open(gt_fname, 'r')
            gt_text = ftxt.read().strip()
            ftxt.close()
            #
            # salida de OCR
            #
            ftxt = open(trans_fname, 'r')
            trans_text = ftxt.read().strip()
            ftxt.close()

            trans_score = distance.nlevenshtein(trans_text, gt_text, method=2)
            print('after ocr:',trans_text,'(',trans_score,')')
            #
            # primera fase: regex
            #
            regex_text = postprocessor.process_with_regex(trans_text)
            regex_score = distance.nlevenshtein(regex_text, gt_text, method=2)
            print('after regex:',regex_text)
            print('after ocr:',regex_text,'(',regex_score,')')
            #
            # we don't need this since we are correcting single lines
            #
            # # USO DE FLAG process_split_word_by_newline
            # flag_pswbn = config.process_split_word_by_newline
            # if flag_pswbn in ("split", "join"):
            #     result_after_pfe = process_format_error.correct_split_word_by_newline(result_after_regex, flag_pswbn,
            #                                                                           language_model)
            #     results_evaluator.save_correct_split_word_by_newline_results(dir_step_2, filename, result_after_pfe)
            #     text_to_procces = text_generator.generate_text_split_words_by_newline(result_after_regex,
            #                                                                           result_after_pfe['tokens'])
            #
            # text_for_split_word_process = text_to_procces
            #
            # # USO DE FLAG correct_split_word
            # flag_csw = config.correct_split_word
            # if (flag_csw in ("any_line", "same_line")):
            #     result_after_pfe_2 = process_format_error.correct_split_word(text_for_split_word_process)
            #     text_to_procces = text_generator.generate_text_split_words(text_for_split_word_process,
            #                                                                result_after_pfe_2['tokens'])
            #fh.write_file(dir_step_1, f'improved_{filename}', text_to_procces)
            #
            # segunda etapa: corrector
            #
            corr_text = postprocessor.correct_errors_process(regex_text, language_model)
            corr_score = distance.nlevenshtein(corr_text, gt_text, method=2)
            print('after corr:',corr_text,'(',corr_score,')')
            #results_evaluator.save_postprocessor_results(dir_step_2, filename, result, text_to_procces)

            #=================================00


            #scores.append(score)
            print(f"{score:8.6f}")
    print('FINISHED ---------------------------------------')
    print('Statistics:')
    S = np.asarray(scores)
    print('\t mean   ', np.mean(S))
    print('\t median ', np.median(S))



#def evaluate_results():
#    results = results_evaluator.get_similarity_between_directories(dir_ground_truth, dir_step_2)
#    results_evaluator.save_similarities_results(dir_results_evaluation, results)

#def process_all_files():
#    filenames = fh.read_directory_files(dir_ocr_outputs)
#    print('procesando todos los archivos con la config')
#    print(config.correct_upper_case, config.correct_upper_case_first_letter, config.process_split_word_by_newline, config.context_direction, config.language_model, config.correct_split_word, config.vocabulary)
#    print('cantidad de archivos a procesar: ' + str(len(filenames)))
#    for filename in filenames:
#        print('archivo: ' + filename + '\n')

# ------------------------------------------------------------------------------- #
def main():
    global language_model
    global postprocessor
    global process_format_error
    global dir_step_1
    global dir_step_2
    global dir_ocr_outputs
    global dir_ground_truth
    global dir_results_evaluation

    language_model = LanguageModel()
    language_model.load_model()

    postprocessor = Postprocessor()
    process_format_error = ProcessFormatError(postprocessor, language_model)

    dir_step_1 = 'local_step_1_outputs'
    dir_step_2 = 'local_step_2_outputs'
    dir_ocr_outputs = 'local_tesseract_training_outputs'
    dir_ground_truth = 'local_luisa_traductions'
    dir_results_evaluation = 'local_results_evaluation'

    postprocessor.load_vocabulary(config.vocabulary)

    # Si no se especifica el archivo a procesar se procesan todos los del directorio de outputs.

    process_file(ARGS.document) if ARGS.document else process_all_files()

    # Evalúa similitud entre todos los archivos
    evaluate_results()

ARGS = build_script_arguments()

main()


